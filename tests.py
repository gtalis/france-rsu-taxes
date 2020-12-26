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

from rsu_grant import RsuGrant
from datetime import date, datetime

# Examples taken from:
# https://mensbridge.fr/fiscalite-pour-les-actions-gratuites/

# Example 1:
# 1000 RSUs granted on June 2010: value 10 euros
# In June 2012, RSUs were vested at 20 euros
# In 2015, RSUs were sold for 50 euros each
# Taxes category: 41%

# Example 2:
# 1000 RSUs granted on June 2013: value 10 euros
# In June 2015, RSUs were vested at 20 euros
# In Sept 2017, RSUs were sold for 50 euros each
# Taxes category: 41%

# Example 3:
# 1000 RSUs granted on Sept 2015: value 10 euros
# In Sept 16, RSUs were vested at 20 euros
# In Jan 2019, RSUs were sold for 50 euros each
# Taxes category: 41%

grant_qty = 1000
grant_vesting_value = 20
grant_selling_value = 50
tmi = 41

grant_vesting_dates = ( datetime(2010, 6, 10),
                        datetime(2013, 6, 10),
                        datetime(2015, 9, 10))
                        
grant_selling_dates = ( datetime(2015, 6, 10),
                        datetime(2017, 9, 10),
                        datetime(2019, 1, 10))
                        
# There's a typo in Example 2
# Total vesting taxes are not 11528.4, but 11582.4
total_vesting_taxes = ( 11440, 11582.4, 7540)
total_selling_taxes = 9000


for i in range(0,3):
	grant = RsuGrant(grant_qty,
					grant_vesting_dates[i],
					grant_vesting_value,
					grant_selling_dates[i],
					grant_selling_value)

	wrong_vesting_taxes = 0
	wrong_gain_loss_taxes = 0

	print("Example " + str(i+1) + ": ")
	print("Total Vesting Value: ... ", grant.total_vesting_value())
	print("Total Selling Value: ... ", grant.total_selling_value())
	print("Vesting Taxes      : ... ",
			grant.vesting_taxes(tmi))
	print("Gain/Loss Taxes    : ... ", grant.gain_loss_taxes())
	print("Total Taxes        : ... ", grant.total_taxes(tmi))
	
	if grant.vesting_taxes(tmi) != total_vesting_taxes[i]:
		print("ERROR: Vesting Taxes are wrong: ")
		print("       Expected: ... ", total_vesting_taxes[i])
		print("       Got     : ... ", grant.vesting_taxes(tmi))
		wrong_vesting_taxes = 1

	if grant.gain_loss_taxes() != total_selling_taxes:
		print("ERROR: Gain/Loss Taxes are wrong: ")
		print("       Expected: ... ", total_selling_taxes)
		print("       Got     : ... ", grant.gain_loss_taxes())
		wrong_gain_loss_taxes = 1
		
	if wrong_vesting_taxes or wrong_gain_loss_taxes:
		print("Test FAILED")
	else:
		print("Test PASSED")
	
	print(" ")			
