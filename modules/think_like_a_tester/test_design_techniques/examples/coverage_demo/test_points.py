# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from points import points_for


def test_a_member_first_order():
    # $30.00: 30 points, doubled to 60, plus 50 for the first order
    assert points_for(3000, member=True, first_order=True) == 110
