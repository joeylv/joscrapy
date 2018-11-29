from scrapy import cmdline
# cmd_str = 'scrapy crawl cnblog'
# cmd_str = 'scrapy crawl topblog'
cmd_str = 'scrapy crawl blog_title --nolog'
cmdline.execute(cmd_str.split(' '))