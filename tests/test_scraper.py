import tempfile
import unittest

from pastpaper.scraper import build_download_tasks
from pastpaper.subjects import SUBJECTS


class DownloadTasksTest(unittest.TestCase):
    def test_new_subject_download_urls(self):
        cases = [
            ('7', '14', 'mathematics-further-9231', '9231-mathematics---further'),
            ('8', '44', 'biology-9700', '9700-biology'),
        ]
        with tempfile.TemporaryDirectory() as out_dir:
            for key, paper, slug, stem in cases:
                with self.subTest(subject=key):
                    _, code, subject_slug = SUBJECTS[key]
                    tasks = build_download_tasks(
                        code, subject_slug, 'A-Level', 'both (qp & ms)',
                        ['s'], ['May-June'], ['26'], [paper], out_dir,
                    )
                    self.assertEqual(len(tasks), 2)
                    for (url, path), kind, label in zip(
                        tasks, ['qp', 'ms'], ['question-paper', 'mark-scheme']
                    ):
                        self.assertEqual(
                            url,
                            f'https://pastpapers.co/api/file/caie/a-level/{slug}/'
                            f'2026-may-june/{stem}-june-2026-{label}-{paper}.pdf?download=1',
                        )
                        self.assertTrue(path.endswith(f'/{kind}/{code}_s26_{kind}_{paper}.pdf'))

    def test_new_subject_sessions_and_unnumbered_reports(self):
        with tempfile.TemporaryDirectory() as out_dir:
            tasks = build_download_tasks(
                '9700', 'Biology-9700', 'A-Level', 'gt (grade threshold)',
                ['m', 'w'], ['March', 'Oct-Nov'], ['25'], ['41', '42'], out_dir,
            )
            self.assertEqual(len(tasks), 2)
            for (url, path), month in zip(tasks, ['march', 'november']):
                self.assertIn(f'9700-biology-{month}-2025-grade-thresholds.pdf', url)
                self.assertTrue(path.endswith('/gt/9700_' + ('m25' if month == 'march' else 'w25') + '_gt.pdf'))

    def test_existing_subject_explicit_numbers_are_unchanged(self):
        with tempfile.TemporaryDirectory() as out_dir:
            papers = ['41', '42', '43', '51', '52', '53']
            tasks = build_download_tasks(
                '9701', 'Chemistry-9701', 'A-Level', 'qp',
                ['s'], ['May-June'], ['26'], papers, out_dir,
            )
            self.assertEqual(len(tasks), len(papers))
            for (url, _), paper in zip(tasks, papers):
                self.assertTrue(url.endswith(f'/9701_s26_qp_{paper}.pdf?download=true'))


if __name__ == '__main__':
    unittest.main()
