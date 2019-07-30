from scrapy import cmdline

cmd_str = 'scrapy crawl csdn'
# cmd_str = 'scrapy crawl cnblog --nolog'
# cmd_str = 'scrapy crawl topblog  --nolog'
# cmd_str = 'scrapy crawl blog_title --nolog'
# cmd_str = 'scrapy crawl cmsblogs --nolog'
cmdline.execute(cmd_str.split(' '))
