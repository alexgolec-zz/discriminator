import heapq
import random

last_employee_was_male = False

class Employee(object):
    def __init__(self, bias, gender=None):
        '''Create a new employee. If the gender is not specified, the gender is
        chosen randomly.'''
        self.history = []
        if gender is None:
            global last_employee_was_male
            if last_employee_was_male:
                self.gender = 'female'
            else:
                self.gender = 'male'
            last_employee_was_male = not last_employee_was_male
            #self.gender = random.choice( ('male', 'female') )
        else:
            self.gender = gender
        self.rating = random.random()
        if self.gender == 'male':
            self.rating *= bias


    def add_event(self, event):
        '''Add a string describing an event to this employee's history.'''
        self.history.append(event)


    def rate(self, bias=1.0):
        return self.rating


    def __lt__(self, other):
        # heapq.heappop() returns the smallest element of the heap in constant
        # time. Since heapq does not provide any way to input a key function, we
        # reverse the ordering of the comparison to make the heap return the
        # largest element instead.
        return other.rate() < self.rate()


    def __str__(self):
        return self.gender


def make_organization(capacities, bias):
    '''Create an organization with the specified levels per capacity. The
    capacities are assumed to be ordered from the capacity of the highest tier
    to that of the lowest. Returns a list of the tiers ordered from lowest to
    highest.'''
    levels = []
    for tier in xrange(len(capacities) - 1, -1, -1):
        if tier != len(capacities) - 1:
            lower_tier = levels[len(capacities) - 2 - tier]
        else:
            lower_tier = None
        levels.append(Level(tier, lower_tier, capacities[tier], bias))
    return levels


def do_promotion_round(organization):
    '''Given an organization as a list ordered from lowest level to highest,
    perform on round of promotions. This consists of the following steps:
     1. Attrite the entire organization.
     2. For each level, promote into the vacancies.'''
    for level in organization:
        level.attrite(0.2)
    for level in reversed(organization):
        level.fill_vacancies()


class Level(object):
    def __init__(self, tier, level_below, capacity, bias):
        self.tier = tier
        self.level_below = level_below
        self.capacity = capacity
        self.employees = []
        self.bias = bias
        self.populate()


    def fill_vacancies(self):
        '''For all vacancies, choose an employee from the lower level to promote
        into this level. If this is the lowest level, then randomly fill all
        vacancies.'''
        if self.level_below is not None:
            for i in xrange(len(self.employees), self.capacity):
                heapq.heappush(self.employees,
                        self.level_below.promote_employee())
        else:
            self.populate()


    def promote_employee(self):
        '''Choose the employee to promote by promoting an employee from the
        lower level. If this level is empty and is not the lowest level, choose
        an employee from the lower level. If the level is the lowest level and '''
        if len(self.employees) != 0:
            return heapq.heappop(self.employees)
        elif self.level_below is not None:
            return self.level_below.promote_employee()
        else:
            self.populate()
            return heapq.heappop(self.employees)


    def populate(self):
        '''Fill any vacancies with employees from a uniformly random
        distribution of genders.'''
        for i in xrange(len(self.employees), self.capacity):
            heapq.heappush(self.employees, Employee(self.bias))


    def add_employee(self, employee):
        '''Place an employee into this level.'''
        self.employees.add(employee)


    def attrite(self, prob):
        '''Lose employees to attrition at the given probability, and yield the
        attrited employees.'''
        # Pop off all the employees from the current heap, attrite them
        # randomly, and then push them into an alternate heap. The popping
        # operation happens in constant time, and since the employees will come
        # off sorted, the pushing operation does so as well.
        scr = []
        while len(self.employees) != 0:
            employee = heapq.heappop(self.employees)
            if random.random() >= prob:
                heapq.heappush(scr, employee)
        self.employees = scr


    def __str__(self):
        ret = []
        ret.append('level' + str(self.tier + 1))
        males = sum(1 for e in self.employees if e.gender == 'male')
        ret.append(' :' + str(males) + ' males, ')
        females = len(self.employees) - males
        ret.append(str(females) + ' females')
        return ''.join(ret)


    def percent_male(self):
        return (float(sum(1 for e in self.employees if e.gender == 'male'))
                / len(self.employees))


    def get_tier(self):
        return self.tier


def main():
    trials = 100
    rounds_per_trial = 100
    num_levels = 9

    outfile = open('data.csv', 'w')
    import csv
    fieldnames = ['bias'] + ['level' + str(i) for i in xrange(0, num_levels)]
    writer = csv.DictWriter(outfile, fieldnames)
    writer.writeheader()

    for bias in xrange(0, 501):
        bias = float(bias) / 1000 + 1.0
        print ' ------------- bias=', bias
        out_dict = {}
        for trial in xrange(0, trials):
            global last_employee_was_male
            last_employee_was_male = random.choice( (True, False) )
            print 'bias =', bias, ', trial =', trial + 1
            organization = make_organization(
                    [2 ** (i + 2) for i in xrange(0, num_levels)], bias=bias)
            for rnd in xrange(0, rounds_per_trial):
                do_promotion_round(organization)

            for level in organization:
                level_key = 'level' + str(level.get_tier())
                if level_key not in out_dict:
                    out_dict[level_key] = []
                out_dict[level_key].append(level.percent_male())
        for key, level_percentages in out_dict.iteritems():
            out_dict[key] = sum(level_percentages) / len(level_percentages)
        out_dict['bias'] = bias
        for key in sorted(out_dict.keys()):
            print key, '-', out_dict[key]
        writer.writerow(out_dict)
        outfile.flush()

if __name__ == '__main__':
    main()
