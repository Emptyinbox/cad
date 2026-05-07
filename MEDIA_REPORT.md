# Media migration report

Generated 2026-05-07.

## Summary

| Category | Count | Status |
|---|---|---|
| Images downloaded | **72** | OK |
| Images missing on live site (404) | 3 | Acceptable — pages will render with alt text only |
| MP4 videos in manifest | 2 | Skipped — should move to YouTube/Vimeo |
| **Total assets in `src/assets/img/`** | 74 | |
| Total disk size | ~177 MB | Most is the two MP4s (108 MB) |

## Missing images (404 on live site)

These are referenced in pages but already broken on the WordPress site too — leave them alone:

- `2025/02/Screenshot-2025-02-17-at-2.04.57` (no extension, broken upload)
- `2025/04/cloud-storage.png`
- `2025/04/microsoft-365-admin.png`

After migration, do a content sweep on `/cloud-computing-services/` and replace the missing icons with the existing `2025/04/cloud-management.png` etc., or commission new ones.

## Videos — recommend hosting elsewhere

GitHub Pages has a 100 MB single-file limit and 1 GB total repo soft limit. The two MP4s violate both intent and limits.

| File | Size | Recommendation |
|---|---|---|
| `Control-Alt-Delete-Pitch-Video.mp4` | 103 MB | Upload to YouTube (unlisted), embed via `<iframe>` in `/about/` and home |
| `IT-Support-Ticket-Submission.mp4` | 5 MB | Upload to YouTube (unlisted), embed where currently used |

**Action you need to take before Phase 8 (deploy):**
1. Upload both MP4s to YouTube (unlisted is fine).
2. Send me the two video IDs.
3. I'll wire the embeds into the affected pages.
4. Delete the local MP4s from `src/assets/img/2024/07/` before commit (they cannot be deleted by the migration sandbox; do this in Finder).

## What got renamed during download

Nothing was renamed — every image kept its original `wp-content/uploads/<year>/<month>/<filename>` path under `src/assets/img/`, so the path rewrites done in Phase 1 (e.g. content references `/assets/img/2024/12/ctrl-alt-delete-office.jpg`) all resolve cleanly.

## Optimization (deferred)

Original JPGs are not yet converted to WebP. That'll happen in Phase 3 when we wire up the 11ty image plugin (`@11ty/eleventy-img`), which generates responsive `srcset` and WebP variants on build. Doing it now and again later would just be wasted work.
