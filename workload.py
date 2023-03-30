from aws_cdk import Environment
from constructs import Construct

from bastion.component import BastionStack
from core import conf


class Workload(Construct):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            aws_env: Environment,
            **kwargs
    ):
        super().__init__(scope, construct_id)

        BastionStack(
            scope,
            construct_id=conf.BASTION_STACK_NAME,
            stack_name=conf.BASTION_STACK_NAME,
            env=aws_env,
        )
