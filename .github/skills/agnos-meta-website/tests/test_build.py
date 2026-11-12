"""Tests of agnos-meta-website's build command: the demo page given or generated, and the output folder (FTR-WEB-001:
RQ-WEB-001, RQ-WEB-002, RQ-WEB-013; ADR-WEB-001: DEC-WEB-002, DEC-WEB-006)."""
import contextlib
import importlib.util
import io
import json
import shutil
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("agnos_meta_website", SKILL_DIR / "scripts" / "build_site.py")
site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site)

VIEWS = ("overview", "graph", "quality", "history", "delivery", "example-requirement", "example-adr", "example-plan")
GIVEN_PAGE = b"<html>given demo page</html>"
GIVEN_JSON = b'{"given": true}'
GIVEN_SCRIPT = b"window.DATA = {};"
# A stand-in for perf_center.py: writes the page and its data files at --out, records its arguments, fails on request.
STUB_GENERATOR = '''import json, sys
from pathlib import Path
args = sys.argv[1:]
out = Path(args[args.index("--out") + 1])
Path(sys.argv[0]).with_name("arguments.json").write_text(json.dumps(args), encoding="utf-8")
if Path(sys.argv[0]).with_name("fail").exists():
    print("generator failure", file=sys.stderr)
    sys.exit(1)
out.write_bytes(b"<html>generated</html>")
out.with_name(out.stem + ".json").write_bytes(b"{}")
out.with_name(out.stem + ".data.js").write_bytes(b"window.DATA = {};")
'''


class Fixture(unittest.TestCase):
    """A demo repository, a given demo page, a stub generator and an output folder holding a file of the owner's."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="agnos-meta-website-build-"))
        self.demo = self.root / "demo-repo"
        process = self.demo / site.PROCESS
        for folder in site.PROCESS_FOLDERS:
            (process / folder).mkdir(parents=True)
        (process / "1.requirements" / "FTR-BKG-001.md").write_bytes(b"### RQ-BKG-001: One requirement\n" + b"x" * 12000)
        (process / site.INDEX).write_bytes(b"x" * 1000)
        self.given = self.root / "given"
        self.given.mkdir()
        (self.given / "PERF-CENTER.html").write_bytes(GIVEN_PAGE)
        (self.given / "PERF-CENTER.json").write_bytes(GIVEN_JSON)
        (self.given / "PERF-CENTER.data.js").write_bytes(GIVEN_SCRIPT)
        self.stub = self.root / "stub" / "perf_center.py"
        self.stub.parent.mkdir()
        self.stub.write_text(STUB_GENERATOR, encoding="utf-8")
        self.saved_generator, site.PERF_CENTER_SCRIPT = site.PERF_CENTER_SCRIPT, self.stub
        self.out = self.root / "agnos.site"
        (self.out / "screens").mkdir(parents=True)
        (self.out / "README.md").write_text("the owner's file", encoding="utf-8")
        (self.out / "screens" / "old.png").write_bytes(b"old")

    def tearDown(self):
        site.PERF_CENTER_SCRIPT = self.saved_generator
        shutil.rmtree(self.root, ignore_errors=True)

    def run_build(self, *extra):
        """(exit code, standard output, error stream) of `build` on the fixture."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = site.main(["build", "--demo", str(self.demo), "--out", str(self.out), *extra])
        return code, out.getvalue(), err.getvalue()

    def snapshot(self):
        """{relative path: bytes} of the output folder."""
        return {str(p.relative_to(self.out)): p.read_bytes() for p in sorted(self.out.rglob("*")) if p.is_file()}


def png_of_size(width, height):
    """A single-colour PNG of the given size. RQ-WEB-019"""
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    rows = (b"\x00" + b"\x20\x40\x80" * width) * height
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


class TestTheScreenSize(Fixture):
    """RQ-WEB-019, DEC-WEB-007: an image at the capture ratio and at least 1291 px wide, or nothing is written."""

    def build_with_screen(self, width, height):
        """(code, stdout, stderr, snapshot before) of a build whose overview.png has the given size."""
        broken = self.root / "assets-screen"
        shutil.rmtree(broken, ignore_errors=True)
        shutil.copytree(site.ASSETS_DIR, broken)
        (broken / "screens" / "overview.png").write_bytes(png_of_size(width, height))
        before = self.snapshot()
        saved, site.ASSETS_DIR = site.ASSETS_DIR, broken
        try:
            result = self.run_build("--demo-page", str(self.given / "PERF-CENTER.html"))
        finally:
            site.ASSETS_DIR = saved
        return (*result, before)

    def test_given_accepted_sizes_when_built_then_each_succeeds(self):
        """RQ-WEB-019: 1291x720, 1936x1080 and 2582x1440 are accepted."""
        for width, height in ((1291, 720), (1936, 1080), (2582, 1440)):
            with self.subTest(size=(width, height)):
                # Given an image of that size
                # When the site is built
                code, _, err, _ = self.build_with_screen(width, height)
                # Then the build succeeds
                self.assertEqual((code, err), (0, ""))

    def test_given_a_wrong_ratio_when_built_then_the_file_is_named_and_nothing_is_written(self):
        """RQ-WEB-019: 1600x1000 (16:10) and 1000x558 (too narrow) are refused."""
        for width, height in ((1600, 1000), (1000, 558)):
            with self.subTest(size=(width, height)):
                # Given an image of that size
                # When the site is built
                code, out, err, before = self.build_with_screen(width, height)
                # Then it fails naming the file, its size and the expected ratio, and writes nothing
                self.assertEqual((code, out), (1, ""))
                self.assertIn(f"overview.png: {width}x{height}", err)
                self.assertIn("1291:720", err)
                self.assertEqual(self.snapshot(), before)


class TestTheSiteFolder(Fixture):
    """RQ-WEB-001, DEC-WEB-006: the site written into the folder, the owner's other files kept."""

    def test_given_valid_assets_when_built_then_the_folder_holds_the_site(self):
        code, out, err = self.run_build("--demo-page", str(self.given / "PERF-CENTER.html"))
        self.assertEqual((code, err), (0, ""))
        self.assertTrue((self.out / "index.html").is_file())
        self.assertEqual(sorted(p.name for p in (self.out / "screens").iterdir()), sorted(f"{v}.png" for v in VIEWS))
        self.assertEqual((self.out / "README.md").read_text(encoding="utf-8"), "the owner's file")
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertRegex(out, r"^agnos-meta-website: \d+ fields in each language, 8 images, index 1/12, "
                                  r"demo page copied; "
                                  r".+ written$")

    def test_given_a_content_error_when_built_then_the_folder_is_unchanged(self):
        before = self.snapshot()
        saved_assets = site.ASSETS_DIR
        broken = self.root / "assets"
        shutil.copytree(saved_assets, broken)
        (broken / "content" / "fr.md").write_text("## page\n\n### title\nSeul\n", encoding="utf-8")
        site.ASSETS_DIR = broken
        try:
            code, out, err = self.run_build("--demo-page", str(self.given / "PERF-CENTER.html"))
        finally:
            site.ASSETS_DIR = saved_assets
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("fr.md: page.description is missing", err)
        self.assertEqual(self.snapshot(), before)


class TestTheDemoPage(Fixture):
    """RQ-WEB-002, DEC-WEB-002: the demo page copied when given, generated otherwise."""

    def test_given_a_demo_page_then_it_is_copied_with_its_data_byte_for_byte(self):
        code, _, _ = self.run_build("--demo-page", str(self.given / "PERF-CENTER.html"))
        self.assertEqual(code, 0)
        self.assertEqual((self.out / "demo" / "PERF-CENTER.html").read_bytes(), GIVEN_PAGE)
        self.assertEqual((self.out / "demo" / "PERF-CENTER.json").read_bytes(), GIVEN_JSON)
        self.assertEqual((self.out / "demo" / "PERF-CENTER.data.js").read_bytes(), GIVEN_SCRIPT)
        self.assertFalse((self.stub.parent / "arguments.json").exists())

    def test_given_no_demo_page_then_it_is_generated_from_the_demo_with_its_history(self):
        code, _, err = self.run_build()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual((self.out / "demo" / "PERF-CENTER.html").read_bytes(), b"<html>generated</html>")
        self.assertTrue((self.out / "demo" / "PERF-CENTER.data.js").is_file())
        arguments = json.loads((self.stub.parent / "arguments.json").read_text(encoding="utf-8"))
        self.assertIn("--history", arguments)
        self.assertIn("--call-graph", arguments)
        self.assertEqual(arguments[arguments.index("--process") + 1], str(self.demo / site.PROCESS))
        self.assertEqual([arguments[i + 1] for i, a in enumerate(arguments) if a == "--sources"],
                         [str(self.demo / source) for source in site.DEMO_SOURCES])

    def test_given_a_failing_generator_then_nothing_is_written(self):
        (self.stub.parent / "fail").write_text("", encoding="utf-8")
        before = self.snapshot()
        code, _, err = self.run_build()
        self.assertEqual(code, 1)
        self.assertIn("agnos-perf-center failed (exit 1): generator failure", err)
        self.assertEqual(self.snapshot(), before)

    def test_given_a_demo_page_without_its_data_then_it_is_reported(self):
        (self.given / "PERF-CENTER.data.js").unlink()
        code, _, err = self.run_build("--demo-page", str(self.given / "PERF-CENTER.html"))
        self.assertEqual(code, 1)
        self.assertIn("PERF-CENTER.data.js does not exist", err)

    def test_given_a_demo_page_of_another_name_then_it_is_reported(self):
        renamed = self.given / "trace.html"
        (self.given / "PERF-CENTER.html").rename(renamed)
        code, _, err = self.run_build("--demo-page", str(renamed))
        self.assertEqual(code, 1)
        self.assertIn("the demo page must be named PERF-CENTER.html", err)


if __name__ == "__main__":
    unittest.main()
