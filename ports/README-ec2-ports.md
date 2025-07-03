Here's the Python code using AWS CDK to create a security group with those rules:

```python
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    App
)
from constructs import Construct

class SecurityGroupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Get the default VPC (or specify your VPC)
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
        
        # Create security group
        security_group = ec2.SecurityGroup(
            self, "MySecurityGroup",
            vpc=vpc,
            description="Security group with custom rules",
            security_group_name="my-custom-sg"
        )
        
        # SSH (TCP 22)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="SSH access"
        )
        
        # HTTP (TCP 80)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="HTTP access"
        )
        
        # HTTPS (TCP 443)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS access"
        )
        
        # MySQL/Aurora (TCP 3306)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(3306),
            description="MySQL/Aurora access"
        )
        
        # Custom TCP 7860-7865 (port range)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp_range(7860, 7865),
            description="Custom TCP 7860-7865"
        )
        
        # Custom TCP 8080
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8080),
            description="Custom TCP 8080"
        )
        
        # Custom TCP 11434
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(11434),
            description="Custom TCP 11434"
        )

# App and stack instantiation
app = App()
SecurityGroupStack(app, "SecurityGroupStack")
app.synth()
```

**Alternative using Boto3** (if you prefer direct AWS SDK):

```python
import boto3

def create_security_group():
    ec2 = boto3.client('ec2')
    
    # Create security group
    response = ec2.create_security_group(
        GroupName='my-custom-sg',
        Description='Security group with custom rules'
    )
    
    security_group_id = response['GroupId']
    print(f"Created security group: {security_group_id}")
    
    # Define ingress rules
    ingress_rules = [
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS access'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 3306,
            'ToPort': 3306,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'MySQL/Aurora access'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 7860,
            'ToPort': 7865,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Custom TCP 7860-7865'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 8080,
            'ToPort': 8080,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Custom TCP 8080'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 11434,
            'ToPort': 11434,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Custom TCP 11434'}]
        }
    ]
    
    # Add ingress rules
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=ingress_rules
    )
    
    print("All ingress rules added successfully!")
    return security_group_id

if __name__ == "__main__":
    sg_id = create_security_group()
```

**To use the CDK version:**
1. Install CDK: `pip install aws-cdk-lib constructs`
2. Run: `cdk deploy`

**To use the Boto3 version:**
1. Install boto3: `pip install boto3`
2. Configure AWS credentials
3. Run the script

Both create the same security group rules you specified, just using different approaches - CDK for infrastructure-as-code or Boto3 for direct API calls.

