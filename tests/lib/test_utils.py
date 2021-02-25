"""
pytest module for lib.utils
"""

# Standard library imports
from pathlib import Path
from os import sep
import random
import string

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.utils import DebugTraceReport
from phibes.lib.utils import decode_name, encode_name
from phibes.lib.utils import find_path_dupes, get_path_tail
from phibes.model import Locker

# Local test imports


class TestEncodeDecodeNames(object):

    def setup_method(self):
        self.name_vals = {
            'gooddogs': 'Z29vZGRvZ3M',
            'mylocker': 'bXlsb2NrZXI',
            'secret_stash': 'c2VjcmV0X3N0YXNo',
            'secret-stash': 'c2VjcmV0LXN0YXNo',
            'gooddog$': 'Z29vZGRvZyQ',
            'names&passwords': 'bmFtZXMmcGFzc3dvcmRz',
            '0reasons!': 'MHJlYXNvbnMh'
        }

    @pytest.mark.positive
    def test_encode_good(self):
        results = {}
        for name in self.name_vals:
            results[name] = encode_name(name)
        assert results == self.name_vals

    @pytest.mark.positive
    def test_decode_good(self):
        results = {}
        for name, scramble in self.name_vals.items():
            results[decode_name(scramble)] = scramble
        assert results == self.name_vals


class TestPathUtils(object):

    def setup_method(self):
        source_path = Path(sep.join(['one', 'two', 'three', 'four', 'five']))
        self.test_set = [
            {
                'path': source_path,
                'nodes': 4,
                'expect': sep.join(['two', 'three', 'four', 'five'])
            },
            {
                'path': source_path,
                'nodes': 3,
                'expect': sep.join(['three', 'four', 'five'])
            },
            {
                'path': source_path,
                'nodes': 2,
                'expect': sep.join(['four', 'five'])
            }
        ]
        dupes_path = Path(sep.join(['one', 'two', 'three', 'three', 'four']))
        self.test_dupes = [
            {'path': dupes_path, 'nodes': 4},
            {'path': dupes_path, 'nodes': 3},
            {'path': dupes_path, 'nodes': 2}
        ]

    @pytest.mark.positive
    def test_get_path_tail_good(self):
        for point in self.test_set:
            assert get_path_tail(
                pth=point['path'], number_of_nodes=point['nodes']
            ) == point['expect'], f"{point=}"

    @pytest.mark.positive
    def test_find_path_dupes_none(self):
        for point in self.test_set:
            assert find_path_dupes(
                full_path=point['path'], number_of_nodes=point['nodes']
            ) == point['expect'], f"{point=}"

    @pytest.mark.positive
    def test_find_path_dupes_exact(self):
        for point in self.test_dupes:
            with pytest.raises(DebugTraceReport):
                find_path_dupes(
                    full_path=point['path'], number_of_nodes=point['nodes']
                ), f"{point=}"

    @pytest.mark.positive
    def test_find_path_dupes_fuzzy(self):
        max_test_length = 20
        safechars = string.ascii_letters + string.digits + "~ -_."
        for match_until in range(3, max_test_length):
            common_prefix = ''.join(
                random.choices(safechars, k=match_until-1)
            )
            # we don't care that the nodes have different lengths
            # control node
            node_1 = common_prefix + '1' + ''.join(
                random.choices(safechars, k=max_test_length)
            )
            # test node matches until len(common_prefix) + 1
            node_a = common_prefix + 'a' + ''.join(
                random.choices(safechars, k=max_test_length)
            )
            test_path = Path(sep.join([node_1, node_a]))
            test_path_reverse = Path(sep.join([node_a, node_1]))
            for num in range(1, max_test_length):
                # all checks up to the unique character should raise
                if num < match_until:
                    with pytest.raises(DebugTraceReport):
                        find_path_dupes(
                            full_path=test_path,
                            number_of_nodes=1,
                            min_match_prefix=num
                        )
                    with pytest.raises(DebugTraceReport):
                        find_path_dupes(
                            full_path=test_path_reverse,
                            number_of_nodes=1,
                            min_match_prefix=num
                        )
                # anything longer should just return
                else:
                    assert node_a == find_path_dupes(
                        full_path=test_path,
                        number_of_nodes=1,
                        min_match_prefix=num
                    )
                    assert node_1 == find_path_dupes(
                        full_path=test_path_reverse,
                        number_of_nodes=1,
                        min_match_prefix=num
                    )
