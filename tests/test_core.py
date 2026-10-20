import csv
import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from campaign_link_doctor.core import check_url, build_url, strip_url
from campaign_link_doctor.cli import main, load_file

BASE = "https://example.org/offers"
GOOD = BASE + "?utm_source=newsletter&utm_medium=email&utm_campaign=autumn"

class TestCampaignLinkDoctor(unittest.TestCase):
    def codes(self, url):
        return [f.code for f in check_url(url).findings]

    def test_no_query_is_clean(self):
        self.assertEqual(self.codes(BASE), [])

    def test_good_utm_is_clean(self):
        self.assertEqual(self.codes(GOOD), [])

    def test_http_warn(self):
        self.assertIn("CLD101", self.codes("http://example.org"))

    def test_bad_scheme(self):
        self.assertIn("CLD001", self.codes("javascript:alert(1)"))

    def test_empty_host(self):
        self.assertIn("CLD001", self.codes("https://"))

    def test_userinfo_rejected(self):
        self.assertIn("CLD001", self.codes("https://user:pass@example.org"))

    def test_utm_duplicate(self):
        self.assertIn("CLD002", self.codes(GOOD + "&utm_source=twitter"))

    def test_duplicate_business_filter_is_valid(self):
        self.assertNotIn("CLD002", self.codes(BASE + "?tag=one&tag=two"))

    def test_missing_utm_requirements_warn(self):
        self.assertIn("CLD103", self.codes(BASE + "?utm_source=story"))

    def test_utm_empty_error(self):
        self.assertIn("CLD004", self.codes(BASE + "?utm_source=&utm_medium=cpc&utm_campaign=fall"))

    def test_campaign_key_case_warn(self):
        self.assertIn("CLD102", self.codes(BASE + "?UTM_Source=x&utm_medium=y&utm_campaign=z"))

    def test_campaign_value_space_warn(self):
        self.assertIn("CLD102", self.codes(BASE + "?utm_source=%20hi%20&utm_medium=a&utm_campaign=c"))

    def test_pii_value(self):
        self.assertIn("CLD003", self.codes(BASE + "?ref=someone%40example.org"))

    def test_pii_key(self):
        self.assertIn("CLD003", self.codes(BASE + "?email=a"))

    def test_secret_key(self):
        self.assertIn("CLD003", self.codes(BASE + "?access_token=fake-value"))

    def test_click_id_info(self):
        self.assertIn("CLD201", self.codes(BASE + "?gclid=opaque"))

    def test_fragment_carries_campaign_warning(self):
        self.assertIn("CLD104", self.codes(BASE + "#utm_source=x"))

    def test_report_never_includes_email(self):
        report = json.dumps(check_url(BASE + "?email=private%40example.org").as_dict())
        self.assertNotIn("private", report)
        self.assertNotIn("example.org", report)

    def test_build_basic(self):
        self.assertEqual(build_url(BASE, source="newsletter", medium="email", campaign="autumn"), GOOD)

    def test_build_preserves_business_query(self):
        link = build_url(BASE + "?sku=22", source="x", medium="y", campaign="z")
        self.assertTrue(link.startswith(BASE + "?sku=22&utm_source=x"))

    def test_build_rejects_old_utm(self):
        with self.assertRaises(ValueError):
            build_url(GOOD, source="a", medium="b", campaign="c")

    def test_build_replaces_old_utm(self):
        link = build_url(GOOD, source="a", medium="b", campaign="c", replace=True)
        self.assertEqual(link.count("utm_source="), 1)

    def test_build_rejects_base_pii(self):
        with self.assertRaises(ValueError):
            build_url(BASE + "?email=a", source="a", medium="b", campaign="c")

    def test_build_rejects_field_email(self):
        with self.assertRaises(ValueError):
            build_url(BASE, source="somebody@example.org", medium="b", campaign="c")

    def test_build_rejects_blank_field(self):
        with self.assertRaises(ValueError):
            build_url(BASE, source=" ", medium="b", campaign="c")

    def test_build_encodes_spaces(self):
        self.assertIn("utm_campaign=big+sale", build_url(BASE, source="x", medium="y", campaign="big sale"))

    def test_strip_click_ids(self):
        clean, n = strip_url(BASE + "?product=1&fbclid=x")
        self.assertEqual((clean, n), (BASE + "?product=1", 1))

    def test_strip_utms(self):
        clean, n = strip_url(GOOD)
        self.assertEqual((clean, n), (BASE, 3))

    def test_strip_sensitive(self):
        clean, n = strip_url(BASE + "?email=user%40example.org&sku=2")
        self.assertEqual((clean, n), (BASE + "?sku=2", 1))

    def test_bad_percent_escape(self):
        self.assertIn("CLD001", self.codes(BASE + "?x=%ZZ"))

    def test_control_character(self):
        self.assertIn("CLD001", self.codes(BASE + "\nabc"))

    def test_too_long(self):
        self.assertIn("CLD001", self.codes(BASE + "a" * 8192))

    def test_load_csv(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "links.csv"
            p.write_text("url,name\n" + GOOD + ",example\n")
            self.assertEqual(load_file(str(p)), [GOOD])

    def test_load_text(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "links.txt"
            p.write_text(GOOD + "\n\n" + BASE + "\n")
            self.assertEqual(load_file(str(p)), [GOOD, BASE])

    def test_load_invalid_csv(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "links.csv"
            p.write_text("not_url\nwhatever\n")
            with self.assertRaises(ValueError):
                load_file(str(p))

    def test_cli_error_exit(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["check", BASE + "?email=a"]), 1)

    def test_cli_good_exit(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["check", GOOD]), 0)

    def test_cli_json_redacts(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(["check", BASE + "?email=user%40example.org", "--format", "json"])
        data = json.loads(out.getvalue())
        self.assertNotIn("user@", out.getvalue())
        self.assertEqual(data["summary"]["links"], 1)

    def test_cli_build(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["build", "--base", BASE, "--source", "a", "--medium", "b", "--campaign", "c"]), 0)
        self.assertIn("utm_source=a", out.getvalue())

    def test_cli_strip(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["strip", GOOD]), 0)
        self.assertEqual(out.getvalue().strip(), BASE)

if __name__ == "__main__":
    unittest.main()

