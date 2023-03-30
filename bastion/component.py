from pathlib import Path

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

from core import conf
from core.constructs.admin_user import AdminUser
from core.constructs.bastion import Bastion
from core.constructs.vpc import VPC


class BastionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        AdminUser(
            self,
            conf.ADMIN_USER_NAME,
            user_name=conf.ADMIN_USER_NAME,
        )

        vpc = VPC(
            self,
            conf.BASTION_VPC_NAME,
            vpc_name=conf.BASTION_VPC_NAME,
        )

        bastion_user_data = ec2.UserData.for_linux()
        bastion_user_data.add_commands(
            Path(__file__).parent.joinpath("./bastion.sh").read_text()
        )
        Bastion(
            self,
            conf.BASTION_INSTANCE_NAME,
            instance_name=conf.BASTION_INSTANCE_NAME,
            instance_type=conf.BASTION_INSTANCE_TYPE,
            vpc=vpc.vpc,
            user_data=bastion_user_data,
        )
