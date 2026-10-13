#!/usr/bin/env python3
"""Download the five Pexels photos used in overlock-seams-that-stop-fraying.html,
upload them to the fashionme.com media library, and write a copy of the HTML whose
<img src> attributes point at the uploaded files.

Run it on a computer that can reach the site, with a WordPress application password
(Users > Profile > Application Passwords). Put the password in the WP_APP_PASSWORD
environment variable or let the script prompt for it, so it does not end up in the
shell history:

    pip install requests
    export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
    python3 wp_media_upload.py --site https://www.fashionme.com --user YOUR_LOGIN \
        --html overlock-seams-that-stop-fraying.html \
        --out overlock-seams-that-stop-fraying.local.html

The five images already hosted on fashionme.com are left as they are. The script can be
re-run: a file that is already in the media library under the same name is reused rather
than uploaded again, and the output file is written after every image, so a run that
stops halfway loses nothing.
"""
import argparse, getpass, mimetypes, os, sys, tempfile
import requests

IMAGES = [
    # (remote src as it appears in the HTML, filename to upload as, alt text)
    ("https://images.pexels.com/photos/7998331/pexels-photo-7998331.jpeg?auto=compress&cs=tinysrgb&w=1600",
     "fm-hands-feeding-fabric-through-an-overlocker.jpg",
     "Hands feeding fabric through an overlocker"),
    ("https://images.pexels.com/photos/38561617/pexels-photo-38561617.jpeg?auto=compress&cs=tinysrgb&w=1600",
     "fm-overlocker-threaded-with-black-thread-close-up.jpg",
     "Close-up of an overlocker threaded with black thread"),
    ("https://images.pexels.com/photos/9850425/pexels-photo-9850425.jpeg?auto=compress&cs=tinysrgb&w=1600",
     "fm-overlocker-tension-dials-and-thread-spools-from-above.jpg",
     "Tension dials on an overlocker seen from above"),
    ("https://images.pexels.com/photos/7256903/pexels-photo-7256903.jpeg?auto=compress&cs=tinysrgb&w=1200",
     "fm-cones-of-black-thread-on-an-overlocker.jpg",
     "Cones of black thread on an overlocker"),
    ("https://images.pexels.com/photos/32641558/pexels-photo-32641558.jpeg?auto=compress&cs=tinysrgb&w=1600",
     "fm-unpicking-a-seam-with-a-seam-ripper.jpg",
     "Unpicking a seam with a seam ripper"),
]

# download at a web-sized width (2560 px wide, like the other "-scaled" images on the site)
def download_url(src):
    return src.split("?")[0] + "?auto=compress&cs=tinysrgb&w=2560"


def find_existing(session, site, filename):
    """Return the source_url of an attachment already uploaded under this filename, or None."""
    stem = os.path.splitext(filename)[0]
    r = session.get(f"{site}/wp-json/wp/v2/media", params={"search": stem, "per_page": 20}, timeout=60)
    r.raise_for_status()
    for m in r.json():
        stored = m.get("media_details", {}).get("file", "") or m.get("source_url", "")
        if os.path.basename(stored) == filename:
            return m["source_url"]
    return None


def upload(session, site, path, filename, alt):
    mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
    with open(path, "rb") as fh:
        r = session.post(f"{site}/wp-json/wp/v2/media",
                         headers={"Content-Disposition": f'attachment; filename="{filename}"',
                                  "Content-Type": mime},
                         data=fh.read(), timeout=120)
    r.raise_for_status()
    media = r.json()
    r2 = session.post(f"{site}/wp-json/wp/v2/media/{media['id']}",
                      json={"alt_text": alt, "title": alt}, timeout=60)
    r2.raise_for_status()
    return r2.json()["source_url"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", help="WordPress application password; defaults to $WP_APP_PASSWORD, else prompts")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    site = a.site.rstrip("/")
    password = a.password or os.environ.get("WP_APP_PASSWORD") or getpass.getpass("Application password: ")

    s = requests.Session()
    s.auth = (a.user, password)
    me = s.get(f"{site}/wp-json/wp/v2/users/me", timeout=60)
    if me.status_code != 200:
        sys.exit(f"Login failed ({me.status_code}): {me.text[:200]}")

    html = open(a.html, encoding="utf-8").read()
    tmp = tempfile.mkdtemp()
    done = 0
    for src, filename, alt in IMAGES:
        if src not in html:
            print(f"skip (not in HTML): {filename}")
            continue
        try:
            local = find_existing(s, site, filename)
            if local:
                print(f"{filename} already in the media library -> {local}")
            else:
                r = requests.get(download_url(src), timeout=120)
                r.raise_for_status()
                path = os.path.join(tmp, filename)
                with open(path, "wb") as fh:
                    fh.write(r.content)
                local = upload(s, site, path, filename, alt)
                print(f"{filename} -> {local}")
        except requests.RequestException as e:
            sys.exit(f"stopped at {filename}: {e}\n{done} image(s) done; the output so far is in {a.out}. "
                     f"Fix the problem and run the same command again.")
        html = html.replace(src, local)
        done += 1
        open(a.out, "w", encoding="utf-8").write(html)   # written after every image so a failed run keeps its progress

    open(a.out, "w", encoding="utf-8").write(html)
    print(f"written {a.out} ({done} image(s) replaced)")


if __name__ == "__main__":
    main()
