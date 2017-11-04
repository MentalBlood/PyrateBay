import urllib3

# If set to False, only torrents with more than 0 seeds will be found
download_all = False

# File for output
out = open('out.txt', 'w')

# Class for storing torrent data
class torrent():
	def __init__(self, title = '', url = '', magnet = '', date = '', size = '', seed_number = '', leech_number = ''):
		self.title = title
		self.url = url
		self.magnet = magnet
		self.date = date
		self.size = size
		self.seed_number = seed_number
		self.leech_number = leech_number
		self.info_string = self.title + '\nurl: ' + self.url + '\nmagnet link: ' + self.magnet + '\nupload date: ' + self.date + '\nsize: ' + self.size + '\nseeds: ' + self.seed_number + '\nleeches: ' + self.leech_number + '\n'

# Function that takes decoded in utf-8 page string and returns torrents with more than 0 seeds
def torrents_from_page(page):
	torrents = []
	while True:
		a = page.find('href="/torrent/')
		if a == -1: return torrents
		page = page[a + 6:]
		b = page.find('"')
		url = page[:b]
		page = page[b:]
		
		page = page[page.find('">') + 2:]
		b = page.find('</')
		title = page[:b]
		page = page[b:]
		
		page = page[page.find('href="magnet') + 6:]
		b = page.find('"')
		magnet = page[:b]
		page = page[b:]

		page = page[page.find('Uploaded') + 9:]
		b = page.find(',')
		date = page[:b].replace('&nbsp;', '-')
		page = page[b:]

		page = page[7:]
		b = page.find(',')
		size = page[:b].replace('&nbsp;', ' ')
		page = page[b:]

		page = page[page.find('align="right">') + 14:]
		b = page.find('<')
		seed_number = page[:b]
		print(seed_number)

		if not download_all:
			# Checks if no seeds for this torrent. By default in search results torrents are sorted by seeds, so if there no seed for this torrent, there will be no of them for the next
			if seed_number == '0': return torrents

		page = page[page.find('">') + 2:]
		b = page.find('<')
		leech_number = page[:b]

		torrents.append(torrent(title, url, magnet, date, size, seed_number, leech_number))
	
	return torrents

def search(query):
	# Getting first page
	s = urllib3.PoolManager().request('GET', 'https://thepiratebay.org/search/' + query, retries = 10).data.decode('utf8')
	
	# Getting number of torrents found and calculating number of pages they are store on (30 torrents per page)
	s = s[s.find('(approx '):]
	torrents_found = s[8:s.find('f') - 1]
	pages_number = int(int(torrents_found) / 30) + 1
	
	# Parsing first page
	parsed = torrents_from_page(s)
	for	torrent in parsed: out.write(torrent.info_string + '\n')
	
	# By default in search results torrents are sorted by seeds, so if there no seed for this torrent, there will be no of them for the next
	if len(parsed) == 30:
		for page in range(1, pages_number):
			s = urllib3.PoolManager().request('GET', 'https://thepiratebay.org/search/' + query + '/' + str(page), retries = 10).data.decode('utf8')
			parsed = torrents_from_page(s)
			for	torrent in parsed: out.write(torrent.info_string + '\n')
			# By default in search results torrents are sorted by seeds, so if there no seed for this torrent, there will be no of them for the next
			if len(parsed) < 30: break
