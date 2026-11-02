import os
import tempfile
import unittest

from task_manager import TaskManager, main


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "tasks.json")
        self.manager = TaskManager(self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_assigns_ids_and_persists(self):
        self.manager.add("First")
        self.manager.add("Second", "high")
        reloaded = TaskManager(self.path)
        self.assertEqual([t["id"] for t in reloaded.tasks], [1, 2])
        self.assertEqual(reloaded.find(2)["priority"], "high")

    def test_add_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            self.manager.add("   ")
        with self.assertRaises(ValueError):
            self.manager.add("Task", "urgent")

    def test_done_and_list_filtering(self):
        self.manager.add("A")
        self.manager.add("B")
        self.manager.set_done(1)
        self.assertEqual([t["id"] for t in self.manager.list()], [2])
        self.assertEqual(len(self.manager.list(show_all=True)), 2)
        self.manager.set_done(1, False)
        self.assertEqual(len(self.manager.list()), 2)

    def test_list_sorted_by_priority(self):
        self.manager.add("low", "low")
        self.manager.add("high", "high")
        self.manager.add("medium")
        self.assertEqual([t["title"] for t in self.manager.list()], ["high", "medium", "low"])

    def test_edit_and_delete(self):
        self.manager.add("Old")
        self.manager.edit(1, "New", "low")
        self.assertEqual(self.manager.find(1)["title"], "New")
        self.assertEqual(self.manager.find(1)["priority"], "low")
        self.manager.delete(1)
        self.assertIsNone(self.manager.find(1))
        with self.assertRaises(KeyError):
            self.manager.delete(1)

    def test_clear_done(self):
        self.manager.add("A")
        self.manager.add("B")
        self.manager.set_done(1)
        self.assertEqual(self.manager.clear_done(), 1)
        self.assertEqual([t["id"] for t in self.manager.tasks], [2])

    def test_cli(self):
        self.assertEqual(main(["--file", self.path, "add", "From CLI", "-p", "high"]), 0)
        self.assertEqual(main(["--file", self.path, "done", "1"]), 0)
        self.assertEqual(main(["--file", self.path, "done", "99"]), 1)
        self.assertTrue(TaskManager(self.path).find(1)["done"])


if __name__ == "__main__":
    unittest.main()
