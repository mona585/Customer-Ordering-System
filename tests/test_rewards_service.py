"""Unit/integration tests — REQ-PRO-02 points redemption."""

from app.extensions import db
from app.services.rewards_service import RewardsService
from tests.conftest import customer_user


class TestRedeemPoints:
    def test_insufficient_points_fails(self, app, customer_user):
        customer_user.points = 100
        db.session.commit()
        result = RewardsService.redeem_points(customer_user.id, option_index=0)
        assert not result.success
        assert "500 points" in result.error

    def test_sufficient_points_issues_voucher(self, app, customer_user):
      customer_user.points = 600 
      db.session.commit()  
      result = RewardsService.redeem_points(customer_user.id, option_index=0)
      assert result.success
      assert result.data["code"].startswith("PTS10-")
      db.session.refresh(customer_user)
      assert customer_user.points == 100
