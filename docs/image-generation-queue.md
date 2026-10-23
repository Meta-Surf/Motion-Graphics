# Cloudflare image queue

Create one UTF-8 JSON manifest in `jobs/pending/<job-name>.json`:

```json
{
  "job_id": "my-short-test-01",
  "title": "Short image test",
  "images": [
    {
      "filename": "scene-01.png",
      "width": 1024,
      "height": 1792,
      "prompt": "Detailed visual description in English or Portuguese."
    }
  ]
}
```

The push-triggered workflow processes queue updates automatically. A scheduled run checks once per hour in case the push did not start the workflow. Generated files appear in a GitHub Actions artifact named with the run ID and expire after seven days. A successful manifest is moved to `jobs/processed/`; a failed job remains pending for retry.

Limits are eight images per manifest, 256–1920 pixels per dimension, filenames without directories, and prompts from 30 to 3,000 characters. Keep prompts as visual descriptions only; never include account credentials or other secrets.
