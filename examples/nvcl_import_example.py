import pyboreholes as pybh
import pyboreholes.importers.nvcl as nvcl
import matplotlib.pyplot as plt
import numpy as np

# Select an endpoint, list endpoints with nvcl.NVCL_ENDPOINTS.keys()
providerkey = 'CSIRO'
endpoint = nvcl.NVCL_ENDPOINTS[providerkey]

# Get a borehole
href, title = nvcl.get_borehole_ids(endpoint['wfsurl'])[0]
print 'First borehole from {0} has id "{1}"'.format(providerkey, title)

# Query the datasets available
ident, name, om_url = nvcl.get_borehole_datasets(endpoint['dataurl'], title)[0]
print '\nBorehole {0}\'s first dataset has ident "{1}" and name "{2}"'.format(title, ident, name)

# Query the analytes available
analytes = nvcl.get_logged_analytes(endpoint['dataurl'], ident)
print '\nDataset {0} has {1} total analytes'.format(name, len(analytes))
an_idents = [i for i, n in analytes]
an_names = [n for i, n in analytes]
print 'The first few analytes read {0}'.format(an_names[0:4])

# Make a request for the data in CSV format, parse and generate a Borehole instance
print '\nThe formatted pyborehole.Borehole object:'
bh = nvcl.get_analytes_as_borehole(nvcl.NVCL_ENDPOINTS['CSIRO']['dataurl'], name, *an_idents[0:4])
print bh

# Generate counts for the mineral groups in the borehole
groups = {}
for name in bh.point_samples['nvcl'].properties['GRP1UTSAS'].values:
    try:
        groups[name] += 1
    except KeyError:
        groups[name] = 0
total = float(sum(groups.values()))
print '\nThe mineral group counts for {0} are:'
for name, value in groups.items():
    print '  -- {0}: {1} samples'.format(name, value)

# Remove invalid group values
del groups['Invalid']
del groups['null']

# Make a pie chart of the mineral group samples down the borehole
fig = plt.figure(figsize=(6, 4))
cmap = plt.get_cmap('RdYlBu')
colors = [cmap(f) for f in np.linspace(0, 1, len(groups))]
plt.pie(groups.values(),
    labels=groups.keys(),
    explode=0.03 * np.ones(len(groups)),
    autopct=lambda x: '{0:1.0f}'.format(x),
    colors=colors)
plt.axis('equal')
fig.savefig('group_fractions.png')