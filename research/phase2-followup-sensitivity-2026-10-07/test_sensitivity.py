import unittest
from pathlib import Path
from sensitivity import RoutedResults, choose_sources


class SensitivityTests(unittest.TestCase):
    def test_only_eligible_a_pairs_are_routed_to_followup(self):
        original=[{'pair_id':'T1-A','config_id':'A'},{'pair_id':'T1-B','config_id':'B'},{'pair_id':'T2-A','config_id':'A'}]
        selected=[{'pair':{'pair_id':'T1-A','config_id':'A'},'attempt':{'directory':'T1-A/attempt-001'}}]
        routes=choose_sources(original,selected,Path('original'),Path('followup'))
        self.assertEqual(routes['T1-A'],Path('followup/T1-A/attempt-001'))
        self.assertEqual(routes['T1-B'],Path('original/T1-B'))
        self.assertEqual(routes['T2-A'],Path('original/T2-A'))

    def test_b_selection_or_unknown_pair_rejected(self):
        original=[{'pair_id':'T1-B','config_id':'B'}]
        for pair in [{'pair_id':'T1-B','config_id':'B'},{'pair_id':'T2-A','config_id':'A'}]:
            with self.assertRaises(ValueError):
                choose_sources(original,[{'pair':pair,'attempt':{'directory':'X'}}],Path('o'),Path('f'))

    def test_routing_missing_pair_fails_instead_of_falling_back(self):
        routed=RoutedResults({'T-A':Path('f/T-A/attempt-001')},Path('derived-status.json'))
        self.assertEqual(routed/'collection-status.json',Path('derived-status.json'))
        with self.assertRaises(KeyError): _=routed/'missing'


if __name__=='__main__': unittest.main()
