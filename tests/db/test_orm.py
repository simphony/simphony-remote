import os
import unittest

from remoteappmanager.db import orm
from remoteappmanager.db.orm import Database, transaction, Accounting
from tests.temp_mixin import TempMixin
from tests import utils


def fill_db(session):
    with transaction(session):
        users = [orm.User(name="user"+str(i)) for i in range(5)]
        session.add_all(users)

        teams = [orm.Team(name="team"+str(i)) for i in range(5)]
        company_team = orm.Team(name='company_team')
        company2_team = orm.Team(name='company2_team')
        teams.append(company_team)
        teams.append(company2_team)
        session.add_all(teams)

        for user, team in zip(users, teams):
            user.teams.append(team)

        # make users 1 3 and 4 part of the company team
        for i in (1, 3, 4):
            users[i].teams.append(company_team)

        # Also check the reverse behavior
        company2_team.users.extend([users[i] for i in (1, 3, 4)])

        # Create a few applications
        apps = [orm.Application(image="docker/image"+str(i))
                for i in range(3)]
        session.add_all(apps)

        policy = orm.ApplicationPolicy(allow_home=False,
                                       allow_common=False,
                                       allow_team_view=False)
        session.add(policy)

        # We want app 0 to be available only to company team
        # app 1 to be available only to user 0
        # and app 2 to be available to user 1

        accountings = [
            orm.Accounting(team=company_team,
                           application=apps[0],
                           application_policy=policy),
            orm.Accounting(team=teams[0],
                           application=apps[1],
                           application_policy=policy),
            orm.Accounting(team=teams[1],
                           application=apps[2],
                           application_policy=policy),
        ]
        session.add_all(accountings)


class TestOrm(TempMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

        self.config = utils.basic_application_config()

    def test_database_init_and_session(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        self.assertIsNotNone(session)

    def test_orm_objects(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            teams = session.query(orm.Team).all()
            users = session.query(orm.User).all()
            company_team = teams[-2]
            company2_team = teams[-1]

            self.assertEqual(teams[0].users[0], users[0])
            self.assertEqual(len(company_team.users), 3)

            # Also check the reverse behavior
            for i in (1, 3, 4):
                self.assertIn(company2_team, users[i].teams)

            # now check if user 1 has access to two applications:
            # app[0] via the company team and app[2] via its own team.
            teams = users[1].teams

            res = session.query(Accounting).filter(Accounting.team_id.in_([
                team.id for team in teams])).all()

            self.assertEqual(len(res), 2)
            self.assertIn("docker/image0",
                          [acc.application.image for acc in res])
            self.assertIn("docker/image2",
                          [acc.application.image for acc in res])

            # User 2 should have access to apps
            teams = users[2].teams

            res = session.query(Accounting).filter(Accounting.team_id.in_([
                  team.id for team in teams])).all()

            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            teams = users[0].teams

            res = session.query(Accounting).filter(Accounting.team_id.in_([
                team.id for team in teams])).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc.application.image for acc in res])

            # User 3 should have access to app 0 only
            teams = users[3].teams

            res = session.query(Accounting).filter(Accounting.team_id.in_([
                team.id for team in teams])).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc.application.image for acc in res])

    def test_apps_for_user(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            users = session.query(orm.User).all()
            res = orm.apps_for_user(session, users[1])
            self.assertEqual(len(res), 2)
            self.assertIn("docker/image0",
                          [acc[1].image for acc in res])
            self.assertIn("docker/image2",
                          [acc[1].image for acc in res])

            res = orm.apps_for_user(session, users[2])
            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            res = orm.apps_for_user(session, users[0])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc[1].image for acc in res])

            res = orm.apps_for_user(session, users[3])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc[1].image for acc in res])
