from src.backend import MailService


class TestEmptyRubbishbin:


    def test_empty_withoutsession(self):
        MailService.logout()
        result = MailService.emptyRubbishBin()
        assert result == False


