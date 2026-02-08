//! PTA Conformance Test Runner
//!
//! This is a Rust-based test runner for the PTA Standards conformance test suite.
//! It executes tests against implementations and produces TAP or JSON output.

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

use anyhow::{Context, Result};
use clap::Parser;
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};

// =============================================================================
// CLI ARGUMENTS
// =============================================================================

#[derive(Parser, Debug)]
#[command(name = "pta-test-runner")]
#[command(about = "Conformance test runner for PTA specifications")]
#[command(version)]
struct Args {
    /// Path to manifest.json file
    #[arg(short, long)]
    manifest: PathBuf,

    /// Run only specific suite (syntax, validation, booking, bql)
    #[arg(short, long)]
    suite: Option<String>,

    /// Filter tests by tags (comma-separated)
    #[arg(short, long)]
    tags: Option<String>,

    /// Run only a specific test by ID
    #[arg(long)]
    test: Option<String>,

    /// Output format (tap, json)
    #[arg(short, long, default_value = "tap")]
    format: OutputFormat,

    /// Command to run for parsing (e.g., "bean-check")
    #[arg(long)]
    parser_cmd: Option<String>,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,

    /// Stop on first failure
    #[arg(long)]
    fail_fast: bool,

    /// Number of parallel jobs
    #[arg(short = 'j', long, default_value = "1")]
    jobs: usize,
}

#[derive(Debug, Clone, clap::ValueEnum)]
enum OutputFormat {
    Tap,
    Json,
}

// =============================================================================
// TEST STRUCTURES
// =============================================================================

#[derive(Debug, Deserialize)]
struct Manifest {
    format: String,
    version: String,
    #[serde(default)]
    description: Option<String>,
    test_directories: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct TestSuite {
    suite: String,
    #[serde(default)]
    description: Option<String>,
    tests: Vec<TestCase>,
}

#[derive(Debug, Clone, Deserialize)]
struct TestInput {
    #[serde(default)]
    inline: Option<String>,
    #[serde(default)]
    file: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
struct TestCase {
    id: String,
    description: String,
    #[serde(default)]
    input: Option<TestInput>,
    expected: Expected,
    #[serde(default)]
    tags: Vec<String>,
    #[serde(default)]
    skip: bool,
    #[serde(default)]
    skip_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
struct Expected {
    #[serde(default)]
    parse: Option<String>,  // "success" or "error"
    #[serde(default)]
    validate: Option<String>,  // "success" or "error"
    #[serde(default)]
    error_contains: Option<Vec<String>>,
    #[serde(default)]
    error_count: Option<usize>,
    #[serde(default)]
    directives: Option<usize>,
}

// =============================================================================
// TEST RESULTS
// =============================================================================

#[derive(Debug, Clone, Serialize)]
struct TestResult {
    id: String,
    description: String,
    status: TestStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    skip_reason: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error_message: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    expected: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    actual: Option<String>,
    duration_ms: f64,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
enum TestStatus {
    Pass,
    Fail,
    Skip,
    Error,
}

#[derive(Debug, Serialize)]
struct TestSummary {
    total: usize,
    passed: usize,
    failed: usize,
    skipped: usize,
    errors: usize,
    duration_ms: f64,
}

#[derive(Debug, Serialize)]
struct JsonOutput {
    summary: TestSummary,
    results: Vec<TestResult>,
}

// =============================================================================
// TEST RUNNER
// =============================================================================

struct TestRunner {
    args: Args,
    manifest_dir: PathBuf,
}

impl TestRunner {
    fn new(args: Args) -> Result<Self> {
        let manifest_dir = args
            .manifest
            .parent()
            .context("Invalid manifest path")?
            .to_path_buf();
        Ok(Self { args, manifest_dir })
    }

    fn run(&self) -> Result<Vec<TestResult>> {
        let manifest = self.load_manifest()?;
        let mut all_results = Vec::new();

        for test_dir in &manifest.test_directories {
            let suite_path = self.manifest_dir.join(test_dir).join("tests.json");
            if !suite_path.exists() {
                if self.args.verbose {
                    eprintln!("Skipping {}: tests.json not found", test_dir);
                }
                continue;
            }

            // Filter by suite if specified
            if let Some(ref suite_filter) = self.args.suite {
                if !test_dir.contains(suite_filter) {
                    continue;
                }
            }

            let suite = self.load_suite(&suite_path)?;
            let results = self.run_suite(&suite, &self.manifest_dir.join(test_dir))?;
            all_results.extend(results);
        }

        Ok(all_results)
    }

    fn load_manifest(&self) -> Result<Manifest> {
        let content = fs::read_to_string(&self.args.manifest)
            .context("Failed to read manifest file")?;
        serde_json::from_str(&content).context("Failed to parse manifest JSON")
    }

    fn load_suite(&self, path: &Path) -> Result<TestSuite> {
        let content = fs::read_to_string(path)
            .with_context(|| format!("Failed to read suite file: {}", path.display()))?;
        serde_json::from_str(&content).context("Failed to parse test suite JSON")
    }

    fn run_suite(&self, suite: &TestSuite, suite_dir: &Path) -> Result<Vec<TestResult>> {
        let mut results = Vec::new();
        let tests: Vec<_> = suite
            .tests
            .iter()
            .filter(|t| self.should_run_test(t))
            .collect();

        let pb = if !self.args.verbose {
            let pb = ProgressBar::new(tests.len() as u64);
            pb.set_style(
                ProgressStyle::default_bar()
                    .template("{spinner:.green} [{bar:40.cyan/blue}] {pos}/{len} {msg}")
                    .unwrap(),
            );
            Some(pb)
        } else {
            None
        };

        for test in tests {
            if let Some(ref pb) = pb {
                pb.set_message(test.id.clone());
            }

            let result = self.run_test(test, suite_dir);

            if self.args.fail_fast && result.status == TestStatus::Fail {
                results.push(result);
                break;
            }

            results.push(result);

            if let Some(ref pb) = pb {
                pb.inc(1);
            }
        }

        if let Some(pb) = pb {
            pb.finish_and_clear();
        }

        Ok(results)
    }

    fn should_run_test(&self, test: &TestCase) -> bool {
        // Filter by specific test ID
        if let Some(ref test_id) = self.args.test {
            if &test.id != test_id {
                return false;
            }
        }

        // Filter by tags
        if let Some(ref tags) = self.args.tags {
            let required_tags: Vec<_> = tags.split(',').map(|s| s.trim()).collect();
            if !required_tags.iter().any(|t| test.tags.contains(&t.to_string())) {
                return false;
            }
        }

        true
    }

    fn run_test(&self, test: &TestCase, suite_dir: &Path) -> TestResult {
        let start = Instant::now();

        // Handle skipped tests
        if test.skip {
            return TestResult {
                id: test.id.clone(),
                description: test.description.clone(),
                status: TestStatus::Skip,
                skip_reason: test.skip_reason.clone(),
                error_message: None,
                expected: None,
                actual: None,
                duration_ms: start.elapsed().as_secs_f64() * 1000.0,
            };
        }

        // Get input content
        let input = match self.get_test_input(test, suite_dir) {
            Ok(input) => input,
            Err(e) => {
                return TestResult {
                    id: test.id.clone(),
                    description: test.description.clone(),
                    status: TestStatus::Error,
                    skip_reason: None,
                    error_message: Some(format!("Failed to read input: {}", e)),
                    expected: None,
                    actual: None,
                    duration_ms: start.elapsed().as_secs_f64() * 1000.0,
                };
            }
        };

        // Execute the test
        let result = self.execute_test(&input, &test.expected);
        let duration_ms = start.elapsed().as_secs_f64() * 1000.0;

        TestResult {
            id: test.id.clone(),
            description: test.description.clone(),
            status: result.0,
            skip_reason: None,
            error_message: result.1,
            expected: result.2,
            actual: result.3,
            duration_ms,
        }
    }

    fn get_test_input(&self, test: &TestCase, suite_dir: &Path) -> Result<String> {
        if let Some(ref input) = test.input {
            if let Some(ref inline) = input.inline {
                Ok(inline.clone())
            } else if let Some(ref file) = input.file {
                let path = suite_dir.join(file);
                fs::read_to_string(&path)
                    .with_context(|| format!("Failed to read input file: {}", path.display()))
            } else {
                anyhow::bail!("Test input has neither inline nor file")
            }
        } else {
            anyhow::bail!("Test has no input")
        }
    }

    fn execute_test(
        &self,
        input: &str,
        expected: &Expected,
    ) -> (TestStatus, Option<String>, Option<String>, Option<String>) {
        // If no parser command specified, just check expectations format
        let Some(ref parser_cmd) = self.args.parser_cmd else {
            return (
                TestStatus::Skip,
                Some("No parser command specified".to_string()),
                None,
                None,
            );
        };

        // Run the parser
        let output = Command::new(parser_cmd)
            .arg("-")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn();

        let mut child = match output {
            Ok(child) => child,
            Err(e) => {
                return (
                    TestStatus::Error,
                    Some(format!("Failed to spawn parser: {}", e)),
                    None,
                    None,
                );
            }
        };

        // Write input to stdin
        use std::io::Write;
        if let Some(ref mut stdin) = child.stdin {
            let _ = stdin.write_all(input.as_bytes());
        }

        let output = match child.wait_with_output() {
            Ok(output) => output,
            Err(e) => {
                return (
                    TestStatus::Error,
                    Some(format!("Failed to wait for parser: {}", e)),
                    None,
                    None,
                );
            }
        };

        let success = output.status.success();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        // Check parse expectation
        if let Some(ref expect_parse) = expected.parse {
            let expect_success = expect_parse == "success";
            if expect_success != success {
                return (
                    TestStatus::Fail,
                    Some(if expect_success {
                        format!("Expected parse success, got error: {}", stderr)
                    } else {
                        "Expected parse error, but parsed successfully".to_string()
                    }),
                    Some(format!("parse: {}", expect_parse)),
                    Some(format!("parse: {}", if success { "success" } else { "error" })),
                );
            }
        }

        // Check error_contains
        if let Some(ref error_patterns) = expected.error_contains {
            for error_pattern in error_patterns {
                if !stderr.contains(error_pattern) {
                    return (
                        TestStatus::Fail,
                        Some(format!(
                            "Expected error containing '{}', got: {}",
                            error_pattern, stderr
                        )),
                        Some(format!("error contains: {}", error_pattern)),
                        Some(format!("actual error: {}", stderr)),
                    );
                }
            }
        }

        (TestStatus::Pass, None, None, None)
    }
}

// =============================================================================
// OUTPUT FORMATTERS
// =============================================================================

fn output_tap(results: &[TestResult]) {
    println!("TAP version 14");
    println!("1..{}", results.len());

    for (i, result) in results.iter().enumerate() {
        let test_num = i + 1;
        let status = match result.status {
            TestStatus::Pass => "ok".green(),
            TestStatus::Fail => "not ok".red(),
            TestStatus::Skip => "ok".yellow(),
            TestStatus::Error => "not ok".red(),
        };

        let suffix = match result.status {
            TestStatus::Skip => format!(
                " # SKIP {}",
                result.skip_reason.as_deref().unwrap_or("Skipped")
            ),
            _ => String::new(),
        };

        println!(
            "{} {} - {}: {}{}",
            status, test_num, result.id, result.description, suffix
        );

        // Print YAML diagnostics for failures
        if result.status == TestStatus::Fail || result.status == TestStatus::Error {
            println!("  ---");
            if let Some(ref msg) = result.error_message {
                println!("  message: {}", msg);
            }
            if let Some(ref expected) = result.expected {
                println!("  expected: {}", expected);
            }
            if let Some(ref actual) = result.actual {
                println!("  actual: {}", actual);
            }
            println!("  ...");
        }
    }
}

fn output_json(results: &[TestResult], duration: Duration) {
    let summary = TestSummary {
        total: results.len(),
        passed: results.iter().filter(|r| r.status == TestStatus::Pass).count(),
        failed: results.iter().filter(|r| r.status == TestStatus::Fail).count(),
        skipped: results.iter().filter(|r| r.status == TestStatus::Skip).count(),
        errors: results.iter().filter(|r| r.status == TestStatus::Error).count(),
        duration_ms: duration.as_secs_f64() * 1000.0,
    };

    let output = JsonOutput {
        summary,
        results: results.to_vec(),
    };

    println!("{}", serde_json::to_string_pretty(&output).unwrap());
}

// =============================================================================
// MAIN
// =============================================================================

fn main() -> Result<()> {
    let args = Args::parse();
    let format = args.format.clone();
    let verbose = args.verbose;

    let start = Instant::now();
    let runner = TestRunner::new(args)?;
    let results = runner.run()?;
    let duration = start.elapsed();

    match format {
        OutputFormat::Tap => output_tap(&results),
        OutputFormat::Json => output_json(&results, duration),
    }

    // Print summary to stderr if verbose
    if verbose {
        let passed = results.iter().filter(|r| r.status == TestStatus::Pass).count();
        let failed = results.iter().filter(|r| r.status == TestStatus::Fail).count();
        let skipped = results.iter().filter(|r| r.status == TestStatus::Skip).count();

        eprintln!();
        eprintln!(
            "Total: {} | {} | {} | {:.2}s",
            format!("{} passed", passed).green(),
            format!("{} failed", failed).red(),
            format!("{} skipped", skipped).yellow(),
            duration.as_secs_f64()
        );
    }

    // Exit with error code if any tests failed
    let has_failures = results.iter().any(|r| r.status == TestStatus::Fail);
    if has_failures {
        std::process::exit(1);
    }

    Ok(())
}
