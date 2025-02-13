#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Test outlier detection."""
import pandas as pd
from src.task.outlier import find_most_isolated_points


class TestOutlier:

    def test_find_most_isolated_points(self):
        df = pd.DataFrame(
            {
                "0": [0, -1, 1, -1, 1, 9],
                "1": [0, 1, 1, -1, -1, 9],
            }
        )
        result = find_most_isolated_points(df, n=1)
        assert result.to_dict() == {"0": {5: 9}, "1": {5: 9}}
