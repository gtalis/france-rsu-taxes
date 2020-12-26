"""
    rsu_grant.py - A python to class to compute French taxes on RSUs
    Copyright (C) 2020 - Gilles Talis
    
    rsu_grant.py is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation, either version 3 of the License,
    or (at your option) any later version.
 
    rsu_grant.py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty
    of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    PURPOSE.  See the GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with rsu_grant.py.
    If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import date, datetime

"""
All the calculation made below originates from:
https://mensbridge.fr/fiscalite-pour-les-actions-gratuites/
https://www.mingzi.fr/mingzi-actualites/taxation-et-fiscalite-des-actions-gratuites/
The task scheme is really cpmplex, so please bear with me if some of
the calculation is not correct

The currency used in this program is EUROS
"""

# Tax period until 27th Sept 2012
TAX_PERIOD_1 = 1
# Tax period from 29th Sept 2012 until August 7th 2015
TAX_PERIOD_2 = 2
# Tax period from Aug 8th 2015 until Dec 31st 2016
TAX_PERIOD_3 = 3
# Tax period after Jan 1st 2017
TAX_PERIOD_4 = 4
# Tax ratio for RSUs gain (sell - vest): 30%
GAIN_TAX_RATIO = 0.3
# Tax ratio for vesting gain for period 1
VESTING_TAX_RATIO_PERIOD_1 = 30

# "Employee contribution" tax ratio: 10% (0% in some cases)
EMPLOYEE_CONTRIB_TAX_RATIO = 0.1

# Vesting gain limit defining the "Employee contribution" tax ratio
# starting from tax period 3 (IN EUROS!!!)
VEST_GAIN_CUTOFF_VALUE = 300000

"""
Social Tax ratios
- Social Tax ratio period 1: 17.2%
- Social Tax ratio period 2: 9,7% (included deductible CSG tax up to 2,8%)
- Social Tax ratio from period 3: 17.2% for vesting gain < 300000
	9,7% (included deductible CSG tax up to 2,8%) for vesting gains > 300000
"""
SOCIAL_TAX_RATIO_HIGH = 0.172
SOCIAL_TAX_RATIO_LOW  = 0.097
DEDUCTIBLE_CSG_TAX_RATIO = 6.8

# vesting taxes
# For period 3, a first level deduction is applied
VESTING_TAXES_DEDUCTION_50	= 0.5
VESTING_TAXES_DEDUCTION_65	= 0.65
VESTING_TAXES_HOLDING_TIME_DAYS = 8*365 + 2

class RsuGrant:

	def __init__(self, number_of_rsus, grant_date, vesting_value, selling_date, selling_value):
		self.number_m = number_of_rsus
		self.grant_date_m = grant_date
		self.rsu_vest_val_m = vesting_value
		self.sell_date_m = selling_date
		self.rsu_sell_val_m = selling_value
		self.vest_val_total_m = number_of_rsus * vesting_value
		self.sell_val_total_m = number_of_rsus * selling_value
		self.sell_gain_total_m = self.sell_val_total_m - self.vest_val_total_m
		# in case of loss between vesting and selling period, applicable taxes
		# scheme is that of the vesting value, but applied to the selling value
		# of the grant
		if (self.sell_gain_total_m < 0):
			self.vest_val_total_m = self.sell_val_total_m
			self.sell_gain_total_m = 0

		# To understand the following, please refer to:
		# https://mensbridge.fr/fiscalite-pour-les-actions-gratuites/
		if self.grant_date_m >= datetime(2017, 9, 27):
			self.tax_period_m = TAX_PERIOD_4
		elif self.grant_date_m >= datetime(2015, 8, 8):
			self.tax_period_m = TAX_PERIOD_3
		elif self.grant_date_m >= datetime(2012, 9, 28):
			self.tax_period_m = TAX_PERIOD_2
		else:
			self.tax_period_m = TAX_PERIOD_1

	def total_vesting_value(self):
		return self.vest_val_total_m

	def total_selling_value(self):
		return self.sell_val_total_m

	def print_tax_period(self):
		if self.tax_period_m == TAX_PERIOD_1:
			return "Tax Period: before 27th Sept 2012"
		elif self.tax_period_m == TAX_PERIOD_2:
			return "Tax Period: between 28th Sept 2012 and 7th Aug 2015"
		elif self.tax_period_m == TAX_PERIOD_3:
			return "Tax Period: between 8th Aug 2015 and 31st Dec 2016"
		else:
			return "Tax Period: after 1st Jan 2017"

	# In french: Fiscalité sur les plus-values de cession
	def gain_loss_taxes(self):
		return self.sell_gain_total_m * GAIN_TAX_RATIO

	# In french: contribution salariale
	def employee_contrib_tax(self):
		# From Aug 8th 2015, employee contribution tax is only due
		# when vesting gain > 300,000 euros
		if self.tax_period_m >= TAX_PERIOD_3 and self.vest_val_total_m < VEST_GAIN_CUTOFF_VALUE:
			return 0
		else:
			return self.vest_val_total_m * 0.1

	# In french: prelevements sociaux
	def social_taxes(self, tmi):
		social_taxes_high = self.vest_val_total_m * SOCIAL_TAX_RATIO_HIGH
		deducted_csg_ratio = DEDUCTIBLE_CSG_TAX_RATIO * tmi / 100
		deducted_taxes_csg_ratio = self.vest_val_total_m * deducted_csg_ratio / 100
		social_taxes_low = self.vest_val_total_m * SOCIAL_TAX_RATIO_LOW - deducted_taxes_csg_ratio

		if self.tax_period_m == TAX_PERIOD_1:
			return social_taxes_high
		elif self.tax_period_m == TAX_PERIOD_2:
			ded_csg_ratio = DEDUCTIBLE_CSG_TAX_RATIO * tmi / 100;
			return social_taxes_low
		elif self.vest_val_total_m < VEST_GAIN_CUTOFF_VALUE:
			return social_taxes_high
		else:
			return social_taxes_low

	# in french: fiscalite des gains d'acquisition pour la periode 1
	def vesting_taxes_period_1(self, tmi):
		if (tmi > VESTING_TAX_RATIO_PERIOD_1):
			return self.vest_val_total_m * VESTING_TAX_RATIO_PERIOD_1 / 100
		else:
			return self.vest_val_total_m * tmi / 100

	# in french: fiscalite des gains d'acquisition pour la periode 2
	def vesting_taxes_period_2(self, tmi):
		return self.vest_val_total_m * tmi / 100

	# in french: fiscalite des gains d'acquisition pour la periode 3
	def vesting_taxes_period_3(self, tmi):
		# Between 2 and 8 years of holding period, tax deduction is 50%
		if (self.sell_date_m -self.grant_date_m).days < VESTING_TAXES_HOLDING_TIME_DAYS:
			return (self.vest_val_total_m * VESTING_TAXES_DEDUCTION_50) * tmi/100
		else:
			# More than 8 years holding period, tax deduction is 65%
			return (self.vest_val_total_m * VESTING_TAXES_DEDUCTION_65) * tmi/100

	# in french: fiscalite des gains d'acquisition pour la periode 4
	def vesting_taxes_period_4(self, tmi):
		if self.vest_val_total_m < VEST_GAIN_CUTOFF_VALUE:
			return self.vesting_taxes_period_3(tmi)
		else:
			return self.vesting_taxes_period_2(tmi)

	# in french: impots sur les gains d'acquisition
	def vesting_taxes_before_social_and_employee_contrib(self, tmi):
		if self.tax_period_m == TAX_PERIOD_1:
			return self.vesting_taxes_period_1(tmi)
		elif self.tax_period_m == TAX_PERIOD_2:
			return self.vesting_taxes_period_2(tmi)
		elif self.tax_period_m == TAX_PERIOD_2:
			return self.vesting_taxes_period_3(tmi)
		else:
			return self.vesting_taxes_period_4(tmi)

	def vesting_taxes(self, tmi):
		return self.vesting_taxes_before_social_and_employee_contrib(tmi) + self.employee_contrib_tax() + self.social_taxes(tmi)

	def total_taxes(self, tmi):
		return self.gain_loss_taxes() + self.vesting_taxes(tmi)
