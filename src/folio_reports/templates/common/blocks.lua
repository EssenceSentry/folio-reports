-- Pandoc writes user-supplied labels. Only fixed macros and validated chart
-- coordinates enter raw LaTeX. Native blocks keep links, math and citations.
local function raw(s) return pandoc.RawInline("latex", s) end
local function latex(s) return pandoc.RawBlock("latex", s) end
local function text(s) return pandoc.Str(s) end

local function command(name, args)
  local out = {raw(name)}
  for _, arg in ipairs(args) do
    table.insert(out, raw("{"))
    table.insert(out, arg)
    table.insert(out, raw("}"))
  end
  return pandoc.Plain(out)
end

local function append(out, blocks)
  for _, block in ipairs(blocks) do table.insert(out, block) end
end

local function environment(name, args, blocks)
  local out = {command("\\begin{" .. name .. "}", args)}
  append(out, blocks)
  table.insert(out, latex("\\end{" .. name .. "}"))
  return out
end

local function required(div, key)
  local value = div.attributes[key]
  if not value or value == "" then
    error("." .. div.classes[1] .. " needs the " .. key .. " attribute")
  end
  return value
end

local function finite(s)
  local x = tonumber(s)
  if not x or x ~= x or math.abs(x) == math.huge then error("Expected a finite number: " .. s) end
  return x
end

local function coordinate(x)
  return string.format("%.6f", x)
end

-- Keep integer differences exact on same-sign axes. An axis crossing zero
-- can exceed the integer range, or even the floating-point range.
local function axis_fraction(x, lo, hi)
  if lo < 0 and hi >= 0 then
    x, lo, hi = x + 0.0, lo + 0.0, hi + 0.0
    if hi - lo == math.huge then x, lo, hi = x / 2, lo / 2, hi / 2 end
  end
  return (x - lo) / (hi - lo)
end

local function axis_position(x, lo, hi)
  return coordinate(axis_fraction(x, lo, hi))
end

local function percent(div, key)
  local x = finite(required(div, key))
  if x < 0 or x > 100 then error(key .. " must be between 0 and 100") end
  return x
end

local function empty_body(div)
  if #div.content ~= 0 then error("." .. div.classes[1] .. " takes attributes and must have an empty body") end
end

local panels = {
  summary={"wash","Executive summary"}, finding={"rail","Finding"},
  recommendation={"wash","Recommendation"}, decision={"rail","Decision"},
  limitation={"caution","Limitation"}, risk={"caution","Risk"},
  note={"line","Note"}, assumption={"line","Assumption"},
  method={"rail","Method"}, definition={"line","Definition"},
}

local function comparison(div)
  local parts = {}
  if #div.content ~= 2 then error(".comparison needs exactly two .column blocks") end
  for i, col in ipairs(div.content) do
    if col.t ~= "Div" or not col.classes:includes("column") then error("Expected a .column with a title") end
    if i == 2 then table.insert(parts, latex("&")) end
    append(parts, environment("FolioColumn", {text(required(col,"title"))}, col.content))
  end
  return environment("FolioColumns", {}, parts)
end

local function trend(div)
  empty_body(div)
  local low, high = required(div,"min"), required(div,"max")
  local a, b = finite(low), finite(high)
  if b <= a then error("Trend max must exceed min") end
  local values = {}
  for token in (required(div,"values") .. ","):gmatch("([^,]*),") do
    local y = finite(token)
    if y < a or y > b then error("Trend observation outside its axis") end
    table.insert(values, y)
  end
  if #values < 2 then error("A trend needs at least two observations") end
  local points = {}
  for i, y in ipairs(values) do
    points[i] = "(" .. coordinate((i-1)/(#values-1)) .. "," .. axis_position(y,a,b) .. ")"
  end
  local chart = command("\\FolioTrend", {text(required(div,"label")), text(low), text(high),
    text(required(div,"start")), text(required(div,"end")), raw(table.concat(points," ")), raw(points[#points])})
  if #values <= 12 then
    return {latex("\\begingroup\\FolioTrendPoints"), chart, latex("\\endgroup")}
  end
  return chart
end


local function cells(width, columns)
  local out = {latex("\\begin{FolioCells}{" .. #columns .. "}{" .. coordinate(width) .. "}")}
  for i, column in ipairs(columns) do
    if i > 1 then table.insert(out,latex("&")) end
    append(out,column)
  end
  table.insert(out,latex("\\end{FolioCells}"))
  return out
end

local function scorecard(d)
  local n = #d.content
  if n < 2 or n > 4 then error("A scorecard needs two to four .measure blocks") end
  local columns={}
  for _, item in ipairs(d.content) do
    if item.t ~= "Div" or not item.classes:includes("measure") then error("Expected .measure inside scorecard") end
    table.insert(columns,environment("FolioMeasure",{text(required(item,"value")),text(required(item,"label"))},item.content))
  end
  return cells((1-.04*(n-1))/n,columns)
end

local function flow(d)
  local list=d.content[1]
  if #d.content~=1 or list.t~="OrderedList" or #list.content<2 or #list.content>4 then
    error(".flow needs one ordered list of two to four short steps")
  end
  local columns={}
  for i,blocks in ipairs(list.content) do
    table.insert(columns,environment("FolioStage",{text(tostring(i))},blocks))
  end
  return cells((1-.04*(#columns-1))/#columns,columns)
end

local function split(s, sep)
  local parts={}
  for item in (s .. sep):gmatch("([^" .. sep .. "]*)" .. sep) do
    table.insert(parts,item:match("^%s*(.-)%s*$"))
  end
  return parts
end

local function heatmap(d)
  local labels=split(required(d,"columns"),"|")
  if #labels<2 or #labels>6 or #d.content<1 then error("Heatmaps need two to six columns and at least one row") end
  local lo,hi=finite(required(d,"min")),finite(required(d,"max"))
  if lo>=hi then error("Heatmap max must exceed min") end
  local out={command("\\FolioHeatTitle",{text(required(d,"label"))}),
    latex("\\noindent\\begin{tabularx}{\\linewidth}{@{}p{.20\\linewidth}*{" .. #labels .. "}{>{\\centering\\arraybackslash}X}}\\toprule")}
  local header={text(d.attributes.stub or "")}
  for _,label in ipairs(labels) do
    table.insert(header,raw("&"));table.insert(header,text(label))
  end
  table.insert(header,raw("\\\\\\midrule"));table.insert(out,pandoc.Plain(header))
  for _,row in ipairs(d.content) do
    if row.t~="Div" or not row.classes:includes("row") then error("Heatmaps expect .row blocks") end
    empty_body(row)
    local values=split(required(row,"values"),",")
    if #values~=#labels then error("Heatmap row length must match columns") end
    local line={text(required(row,"label"))}
    for _,s in ipairs(values) do
      local x=finite(s)
      if x<lo or x>hi then error("Heatmap observation outside its scale") end
      local shade=math.floor(5+31*axis_fraction(x,lo,hi)+.5)
      table.insert(line,raw("&\\cellcolor{FolioAccent!" .. shade .. "!white}"))
      table.insert(line,text(s))
    end
    table.insert(line,raw("\\\\"));table.insert(out,pandoc.Plain(line))
  end
  table.insert(out,latex("\\bottomrule\\end{tabularx}"))
  return out
end

local function intervalplot(d)
  local lo, hi = finite(required(d,"min")), finite(required(d,"max"))
  if hi <= lo then error("Interval plot max must exceed min") end
  if #d.content == 0 then error("Interval plot needs at least one .row") end

  local out = {latex("\\begingroup")}
  if d.attributes.reference then
    local ref = finite(d.attributes.reference)
    if ref < lo or ref > hi then error("Reference outside its axis") end
    table.insert(out, command("\\FolioRangeReference", {raw(axis_position(ref,lo,hi)), text(d.attributes.reference)}))
  end
  table.insert(out, latex("\\begin{FolioRanges}"))
  table.insert(out, pandoc.Plain({raw("\\multicolumn{4}{@{}p{\\linewidth}@{}}{\\FolioRangeTitle{"),
    text(required(d,"label")), raw("}}\\\\\\midrule")}))
  table.insert(out, pandoc.Plain({text(d.attributes.stub or "Group"), raw("&\\FolioRangeAxis{"),
    text(d.attributes.min), raw("}{"), text(d.attributes.max), raw("}&"), text("Estimate"), raw("&"),
    text(d.attributes["interval-label"] or "Interval"), raw("\\\\\\midrule\\endhead")}))
  for _, row in ipairs(d.content) do
    if row.t ~= "Div" or not row.classes:includes("row") then error("Interval plot expects .row blocks") end
    empty_body(row)
    local l, v, h = finite(required(row,"low")), finite(required(row,"value")), finite(required(row,"high"))
    if l > v or v > h then error("Expected low <= value <= high") end
    if l < lo or h > hi then error("Interval plot observation outside its axis") end
    local mark = "\\FolioRangeMark{" .. axis_position(l,lo,hi) .. "}{" ..
      axis_position(v,lo,hi) .. "}{" .. axis_position(h,lo,hi) .. "}"
    table.insert(out, pandoc.Plain({text(required(row,"label")), raw("&" .. mark .. "&"),
      text(row.attributes.value), raw("&"), text("[" .. row.attributes.low .. ", " .. row.attributes.high .. "]"),
      raw("\\\\")}))
  end
  table.insert(out, latex("\\bottomrule\\end{FolioRanges}\\endgroup"))
  return out
end

local function distribution(d)
  empty_body(d)
  local lower,upper = finite(required(d,"min")),finite(required(d,"max"))
  local nums = split(required(d,"summary"),",")
  if #nums~=5 or upper<=lower then error("Box plot needs an increasing axis and five ordered summary values") end
  local coords={}
  local previous=lower
  for _,s in ipairs(nums) do
    local x=finite(s)
    if x<previous or x>upper then error("Box plot summary must be ordered and within its axis") end
    table.insert(coords,raw(axis_position(x,lower,upper)))
    previous=x
  end
  local args={text(required(d,"label")),text(table.concat(nums," / ")),text(d.attributes.min),text(d.attributes.max)}
  for _,v in ipairs(coords) do table.insert(args,v) end
  return command("\\FolioDistribution",args)
end

-- Keep Pandoc's native tables, alignment, captions and repeating headers.
local function table_layout(d)
  local tab = d.content[1]
  if not tab or tab.t ~= "Table" or #d.content > 2 then
    error("table-layout expects a table and an optional note paragraph")
  end
  local note = d.content[2]
  if note and note.t ~= "Para" then error("A table note must be a paragraph") end

  local percent = (d.attributes.width or "100%"):match("^([%d.]+)%%$")
  if not percent then error("Table width must be a percentage") end
  local measure = finite(percent) / 100
  if measure <= 0 or measure > 1 then
    error("Table width must be greater than 0% and at most 100%")
  end

  local widths = split(required(d, "widths"), ",")
  local specs = tab.colspecs
  if #widths ~= #specs then error("Supply one width for each table column") end
  local largest = 0
  for i, part in ipairs(widths) do
    widths[i] = finite(part)
    if widths[i] <= 0 then error("Column widths must be positive") end
    largest = math.max(largest, widths[i])
  end
  -- Normalize before summing so equally large finite weights stay usable.
  local total = 0
  for i, weight in ipairs(widths) do
    widths[i] = weight / largest
    total = total + widths[i]
  end
  for i, spec in ipairs(specs) do specs[i] = {spec[1], widths[i] / total} end
  tab.colspecs = specs
  local content = {tab}
  if note then append(content, environment("FolioTableNote", {}, {note})) end
  return environment("FolioTable", {text(coordinate(measure))}, content)
end

local handlers = {
  ["table-layout"]=table_layout,
  scorecard=scorecard, flow=flow, intervalplot=intervalplot, heatmap=heatmap, distribution=distribution,
  appendix=function(d) empty_body(d); return latex("\\clearpage\\appendix\\setcounter{secnumdepth}{1}") end,
  metric=function(d) return environment("FolioMetric", {text(required(d,"value"))}, d.content) end,
  pullquote=function(d) return environment("FolioQuote", {text(d.attributes.by or "")}, d.content) end,
  source=function(d) return environment("FolioSource", {}, d.content) end,
  milestone=function(d) return environment("FolioEntry", {text(required(d,"when"))}, d.content) end,
  action=function(d) return environment("FolioEntry", {text(required(d,"owner"))}, d.content) end,
  signature=function(d) return environment("FolioSignature", {text(required(d,"name"))}, d.content) end,
  check=function(d)
    local marks = {open="\\(\\square\\)",done="\\(\\boxtimes\\)"}
    local mark = marks[d.attributes.state or "open"]
    if not mark then error("Check state must be open or done") end
    return environment("FolioCheck", {raw(mark)}, d.content)
  end,
  comparison=comparison, trend=trend,
  divider=function(d) empty_body(d); return command("\\FolioDivider",{text(required(d,"title"))}) end,
  pagebreak=function(d) empty_body(d); return latex("\\clearpage") end,
  bar=function(d)
    empty_body(d)
    local v=percent(d,"value")
    return command("\\FolioBar",{text(required(d,"label")),text(d.attributes.value .. "%"),raw(coordinate(v/100))})
  end,
  interval=function(d)
    empty_body(d)
    local l,v,h=percent(d,"low"),percent(d,"value"),percent(d,"high")
    if l>v or v>h then error("Expected low <= value <= high") end
    local caption = d.attributes.value .. "% (" .. d.attributes.low .. "–" .. d.attributes.high .. "%)"
    return command("\\FolioInterval",{text(required(d,"label")),text(caption),
      raw(coordinate(l/100)),raw(coordinate(v/100)),raw(coordinate(h/100))})
  end,
}

function Span(s)
  if not s.classes:includes("status") then return nil end
  local result={raw("\\FolioStatus{")}
  append(result,s.content)
  table.insert(result,raw("}"))
  return result
end

function Div(div)
  for _, class in ipairs(div.classes) do
    if panels[class] then
      local spec=panels[class]
      return environment("FolioPanel",{text(spec[1]),text(div.attributes.title or spec[2])},div.content)
    end
    if handlers[class] then return handlers[class](div) end
  end
end

local function read_tex(path)
  local f,msg=io.open(path,"r")
  if not f then error(msg) end
  local content=f:read("*a")
  f:close()
  return latex(content)
end

function Meta(meta)
  local style=pandoc.utils.stringify(meta["folio-style-preview"] or meta["folio-style"] or "classic")
  if not style:match("^[a-z][a-z0-9-]*$") then error("Invalid folio-style name") end
  local preamble = pandoc.MetaBlocks({read_tex("style.tex"),read_tex("layout.tex"),
    read_tex("components.tex"),read_tex("styles/" .. style .. ".tex")})
  if meta["folio-cover"] == true or pandoc.utils.stringify(meta["folio-cover"] or "") == "true" then
    table.insert(preamble,latex("\\let\\FolioInnerTitle\\maketitle\\renewcommand{\\maketitle}{\\thispagestyle{empty}\\vspace*{.16\\textheight}\\FolioInnerTitle\\clearpage}"))
  end
  local includes=meta["header-includes"]
  if not includes then
    meta["header-includes"]=preamble
  else
    -- Both a single author header and YAML lists are accepted by Pandoc.
    local list=pandoc.MetaList({preamble})
    if includes.t == "MetaList" then
      for _, item in ipairs(includes) do table.insert(list,item) end
    else table.insert(list,includes) end
    meta["header-includes"]=list
  end
  return meta
end
