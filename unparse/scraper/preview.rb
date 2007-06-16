#!/usr/bin/ruby -w

require 'rubygems'
require 'RMagick'

include Magick

(infile, outfile, width, height) = ARGV

width ||= 400
height ||= 300

width = width.to_i
height = height.to_i

pdf = ImageList.new(infile)
preview = Image.new(width,height) {self.background_color = "#ddffff"}

cover = pdf.shift
cover.resize_to_fit!(width * 2, height * 2)
cover.border!(1, 1, 'black')
cover.background_color = 'none'
shadow = cover.dup.color_reset!("#88aaaa")
shadow.background_color = 'none'
cover.rotate!(-10)
shadow.rotate!(-10)
cover_left = (width - cover.columns) * 0.5
cover_top = (height - cover.rows) * 0.6
preview.composite! shadow, cover_left + width * 0.03, cover_top + width * 0.03, OverCompositeOp
preview.composite! cover, cover_left, cover_top, OverCompositeOp

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
preview.write(outfile)

