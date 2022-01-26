from src.backend import MailService

class TestScenarios:

    def test_scenario_no1(self):
        # login -> check if correct
        is_loggedin = MailService.login('testkonto132@onet.pl', 'Aa123456')
        assert is_loggedin == True

        is_empty = MailService.emptyRubbishBin()
        assert is_empty == 'usunięto'

        is_loggedout = MailService.logout()
        assert is_loggedout == 'logout correctly'

        try_empty_trash = MailService.emptyRubbishBin()
        assert try_empty_trash == False
