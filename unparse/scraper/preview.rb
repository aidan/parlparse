#!/usr/bin/ruby -w

require 'rubygems'
require 'RMagick'

include Magick

(infile, outfile, width, height) = ARGV

width ||= 300
height ||= 700

width = width.to_i
height = height.to_i

pdf = ImageList.new(infile)
preview = Image.new(width,height) {self.background_color = "#ddffff"}

cover = pdf.shift
cover.resize_to_fit!(width * 1.7, height * 1.7) # zoom
cover.border!(1, 1, 'black')
cover.background_color = 'none'
shadow = cover.dup.color_reset!("#88aaaa")
shadow.background_color = 'none'
cover.rotate!(-10) # angle of rotation
shadow.rotate!(-10)
cover_left = (width - cover.columns) * 0.18 # 0 is left of page visible, 1 is right visible
cover_top = (height - cover.rows) * 0.1 # 0 is top of page visible, 1 is bottom visible
preview.composite! shadow, cover_left + width * 0.03, cover_top + width * 0.03, OverCompositeOp
preview.composite! cover, cover_left, cover_top, OverCompositeOp

if false
(pdf.length - 1).downto(0) do |i|
	offset = 10 + (i*20);
	next if offset > width
	page = pdf[i]
	page.resize_to_fit!(width * 0.4, height * 0.4)
	page.border!(1, 1, 'black')
	page.fuzz = '100%' # make transparency apply to everything
	# Is this really the best way to set alpha over the entire image? Ugh.
	page = page.transparent('white', (Magick::TransparentOpacity-Magick::OpaqueOpacity).abs * 0.35)
	page.background_color = 'none'
	page.rotate!(20)
	preview.composite! page, offset, height * 0.5, OverCompositeOp
end
end
preview.write(outfile)

