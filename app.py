#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_cloud9.cdk_cloud9_stack import CdkCloud9Stack


app = cdk.App()
CdkCloud9Stack(app, "cdk-cloud9")

app.synth()
