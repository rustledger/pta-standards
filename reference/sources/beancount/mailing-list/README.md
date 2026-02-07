# Beancount Mailing List Archive

## Access Points

The Beancount mailing list is hosted on Google Groups and mirrored at mail-archive.com.

| Source | URL |
|--------|-----|
| Google Groups | https://groups.google.com/g/beancount |
| Mail Archive | https://www.mail-archive.com/beancount@googlegroups.com/ |

## Searching

### Google Groups Search
```
site:groups.google.com/g/beancount <search terms>
```

### Mail Archive Search
```
site:mail-archive.com/beancount@googlegroups.com <search terms>
```

## Bulk Download

Unfortunately, there is no official bulk download option for the mailing list.

### Options for archiving:
1. **Google Takeout** - If you're a member, you may be able to export via Google Takeout
2. **Manual scraping** - Use wget/curl to mirror mail-archive.com pages
3. **NNTP** - Some archives may be available via NNTP

### Scraping example (mail-archive.com):
```bash
# Mirror individual message pages (respect rate limits)
wget --wait=1 --recursive --level=1 \
  "https://www.mail-archive.com/beancount@googlegroups.com/"
```

## Notable Threads

Key discussions that clarify spec behavior:

| Topic | URL | Description |
|-------|-----|-------------|
| TBD | TBD | Add notable threads as found during validation |

## Statistics

- Archive available from: ~2014
- Estimated messages: 7000+
- Primary contributor: Martin Blais (author)
