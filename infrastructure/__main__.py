"""An AWS Python Pulumi program"""

import pulumi
import json
import pulumi_aws as aws


config = pulumi.Config()
db_username = "root"
db_password = "nomelase"

default_vpc = aws.ec2.DefaultVpc("default-vpc", tags={
    "Name": "Default VPC",
})

default_az1 = aws.ec2.DefaultSubnet("default-az-1",
    availability_zone="us-west-2a",
    tags={
        "Name": "Default subnet for us-west-2a",
    }
)

default_az2 = aws.ec2.DefaultSubnet("default-az-2",
    availability_zone="us-west-2b",
    tags={
        "Name": "Default subnet for us-west-2b",
    }
)

default_az3 = aws.ec2.DefaultSubnet("default-az-3",
    availability_zone="us-west-2c",
    tags={
        "Name": "Default subnet for us-west-2c",
    }
)

subnet_ids = pulumi.Output.all(default_az1.id, default_az2.id, default_az3.id).apply(lambda az: f"{az[0]},{az[1]},{az[2]}")

vpc_to_rds = aws.ec2.SecurityGroup("vpc-to-rds",
    description="Allow the resources inside the VPC to communicate with postgres RDS instance",
    vpc_id=default_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=5432,
        to_port=5432,
        protocol="tcp",
        cidr_blocks=[default_vpc.cidr_block],
    )])

rds = aws.rds.Instance("rds-instance",
    allocated_storage=10,
    engine="mysql",
    engine_version="8",
    instance_class="db.t2.micro",
    name="silicorn",
    password="nomelase",
    skip_final_snapshot=True,
    username="root",
    vpc_security_group_ids=[vpc_to_rds.id])

instance_profile_role = aws.iam.Role("beanstalk-master",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Sid": "",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
        }],
    }))

eb_policy_attach = aws.iam.RolePolicyAttachment("eb-policy-attach",
    role=instance_profile_role.name,
    policy_arn="arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier")

instance_profile = aws.iam.InstanceProfile("eb-ec2-instance-profile", role=instance_profile_role.name)

conn = pulumi.Output.all(rds.address, db_password).apply(lambda out: f"mysql+mysqlconnector://root@localhost:3316/silicorn")

eb_app = aws.elasticbeanstalk.Application("test-deploy", description="Testing FastAPI app deployment")

eb_env = aws.elasticbeanstalk.Environment("Test-deploy-env",
    application=eb_app.name,
    solution_stack_name="64bit Amazon Linux 2 v3.2.1 running Python 3.8",
    settings=[
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:elasticbeanstalk:environment:proxy",
            name="ProxyServer",
            value="apache"
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:autoscaling:launchconfiguration",
            name="IamInstanceProfile",
            value=instance_profile.name
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:ec2:vpc",
            name="VPCId",
            value=default_vpc.id,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:ec2:vpc",
            name="Subnets",
            value=subnet_ids,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:elasticbeanstalk:application:environment",
            name="CONNECTION_STRING",
            value=conn,
        ),
    ])

pulumi.export('connection_string', conn)
