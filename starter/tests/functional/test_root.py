from . import FuncTest

class TestRoot(FuncTest):
    def test_index(self):
        res = self.testapp.get('/', status=200)
        res.mustcontain(
            '<h1>Pyramid App</h1>'
        )
        self.assertEqual(res.click('Learn more').status_int, 200)

    def test_about(self):
        res = self.testapp.get('/about.html', status=200)
        res.mustcontain('<h1>About</h1>')
