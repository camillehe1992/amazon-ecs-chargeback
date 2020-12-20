# task.py

from pricing import Pricing

pricing_dict = {}
region_table = {}


class Task:
    """
    A Task class for each item in DynamoDB table
    """

    def __init__(self, item):
        # general
        self.groupName = item['groupName']
        self.cpu = item['cpu']
        self.memory = item['memory']
        # pricing
        self.region = item['region']
        self.launchType = item['launchType']
        self.osType = item['osType']
        # duration
        self.startedAt = item['startedAt']
        self.stoppedAt = item['stoppedAt']
        self.runTime = item['runTime']

        self.pricing = Pricing('AmazonEC2')

    def duration(self, meter_start, meter_end, now):
        mRuntime = 0.0
        return mRuntime

    def update_pricing_dict(self, key, ec2_cpu, ec2_mem, ec2_cost):
        pass

    def split_cost_by_weight(self, pricing_key, runTime, ec2_cpu2mem_weight=0.5):
        # Split EC2 cost bewtween memory and weights
        cpu_charges = ((float(self.cpu)) / 1024.0 / pricing_key['cpu']) * (
            float(pricing_key['cost']) * ec2_cpu2mem_weight) * (runTime/60.0/60.0)
        mem_charges = ((float(self.memory)) / 1024.0 / pricing_key['memory']) * (
            float(pricing_key['cost']) * (1.0 - ec2_cpu2mem_weight)) * (runTime/60.0/60.0)
        return (mem_charges, cpu_charges)

    def cost_of_ec2task(self, runTime):
        global pricing_dict
        global region_table

        pricing_key = '_'.join(
            ['ec2', self.region, self.launchType, self.osType])
        if pricing_key not in pricing_dict:
            (ec2_cpu, ec2_mem, ec2_cost) = self.pricing.ec2_pricing(
                region=region_table[self.region],
                instance_type=self.launchType,
                tenancy='Shared',
                ostype=self.osType)
            self.update_pricing_dict(pricing_key, ec2_cpu, ec2_mem, ec2_cost)

        (mem_charges, cpu_charges) = self.split_cost_by_weight(
            pricing_dict[pricing_key], runTime)

        return (mem_charges, cpu_charges)

    def get_datetime_start_end(self, now, month, days, hours):
        pass


class Charge:
    def __init__(self, tasks, meter_start, meter_end, now):
        self.tasks = tasks
        self.meter_start = meter_start
        self.meter_end = meter_end
        self.now = now
        self.mem_cost = 0.0
        self.cpu_cost = 0.0

    def cost_of_service(self):
        for task in self.tasks:
            runTime = task.duration(self.meter_start, self.meter_end, self.now)
            ec2_mem_charges, ec2_cpu_charges = task.cost_of_ec2task(runTime)
            self.mem_cost += ec2_mem_charges
            self.cpu_cost += ec2_cpu_charges

        return (ec2_mem_charges, ec2_cpu_charges)
