#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { RegulusAiStack } from '../lib/cdk-first-stack';

const app = new cdk.App();
new RegulusAiStack(app, 'RegulusAiStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
  // env: { account: '098667488212', region: 'eu-central-1' },
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_ACCOUNT }
});