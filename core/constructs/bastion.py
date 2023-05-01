from typing import Optional

from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam, Tags,
)
from cdk_ec2_key_pair import KeyPair
from constructs import Construct


class Bastion(Construct):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            instance_name: str,
            instance_type: str,
            vpc: ec2.IVpc,
            user_data: ec2.UserData,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id)

        # 4. Security group de instancia
        self._instance_security_group = ec2.SecurityGroup(
            self,
            "InstanceSecurityGroup",
            security_group_name=f"{construct_id}-security-group",
            vpc=vpc,
            allow_all_outbound=True,
            description="Bastion instance security group",
        )
        self._instance_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allows SSH access from any IP"
        )

        # 5. KeyPair de instancia
        self._instance_key_pair = KeyPair(
            self,
            "InstanceKeyPair",
            name=f"{construct_id}-key-pair",
            resource_prefix=f"{construct_id}",
            store_public_key=True,
        )

        # 6. Rol de instancia
        self._instance_role = iam.Role(
            self,
            "InstanceRole",
            role_name=f"{construct_id}-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        # 7. Permisos de rol de instancia
        self._instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )
        # SSM Agent
        self._instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        # 8. Tags de rol de instancia
        Tags.of(self._instance_role).add(
            key='RoleName',
            value='ec2-admin-role',
        )

        # 2. Storage de instancia
        self._root_volume: ec2.BlockDevice = ec2.BlockDevice(
            device_name='/dev/xvda',
            volume=ec2.BlockDeviceVolume.ebs(
                volume_size=8,
                volume_type=ec2.EbsDeviceVolumeType.GP2,
            ),
        )

        self._instance = ec2.Instance(
            self,
            "Instance",
            instance_name=instance_name,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            # 9. Asignación de rol de instancia
            role=self._instance_role,
            # 4. Security group de instancia
            security_group=self._instance_security_group,
            key_name=self._instance_key_pair.key_pair_name,
            # 1. tipo de instancia
            instance_type=ec2.InstanceType(instance_type),
            # 2. storage de instancia
            block_devices=[self._root_volume],
            machine_image=ec2.MachineImage.from_ssm_parameter(
                # Ubuntu LTS
                parameter_name="/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id",
                os=ec2.OperatingSystemType.LINUX,
            ),
            # 1. user-data de instancia
            user_data=user_data,
        )

        # 3. Tags de instancia
        Tags.of(self._instance).add(
            key='Name',
            value='Jenkins',
        )

    @property
    def instance_role(self):
        return self._instance_role

    @property
    def instance_security_group(self):
        return self._instance_security_group

    @property
    def instance_key_pair(self):
        return self._instance_key_pair

    @property
    def instance(self):
        return self._instance
