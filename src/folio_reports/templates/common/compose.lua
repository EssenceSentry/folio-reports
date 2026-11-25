-- Flow ordinary Markdown in columns, with native evidence on the full grid.
local function latex(text) return pandoc.RawBlock("latex", text) end
local function raw_tex(block)
  return block.t == "RawBlock" and (block.format == "tex" or block.format == "latex")
end
local function keeps_list(block)
  return block.t == "Div" and block.classes:includes("keep-together")
end

local function figure(block)
  if block.t == "Figure" then return true end
  if raw_tex(block) then
    return block.text:match("^\\begin{figure}") ~= nil
  end
  return block.t == "Para" and #block.content == 1 and block.content[1].t == "Image"
end

local function prose(block, column_math)
  if not block then return false end
  if block.t == "Para" then
    if figure(block) then return false end
    if not column_math then
      for _, inline in ipairs(block.content) do
        if inline.t == "Math" and inline.mathtype == "DisplayMath" then return false end
      end
    end
    return true
  end
  if block.t == "Div" then
    return keeps_list(block) or block.identifier == "refs"
  end
  if raw_tex(block) then
    return block.text:match("^\\columnbreak%s*$") ~= nil
  end
  return block.t == "BulletList" or block.t == "OrderedList" or block.t == "BlockQuote"
    or block.t == "CodeBlock" or block.t == "DefinitionList" or block.t == "LineBlock"
end

local function span_table(block)
  local specs = block.colspecs
  local weights, total = {}, 0
  for i, spec in ipairs(specs) do
    local width = spec[2] or 0
    weights[i] = width > 0 and width or 1 / #specs
    total = total + weights[i]
  end
  local cumulative, left = 0, 0
  for i, spec in ipairs(specs) do
    cumulative = cumulative + weights[i]
    if #specs <= 100 then
      -- Pandoc's TeX writer rounds widths to hundredths. Round cumulative boundaries
      -- to retain the full measure and leave at least one part for each column.
      local rounded = math.floor(100 * cumulative / total + 0.5)
      local right = math.max(left + 1, math.min(rounded, 100 - (#specs - i)))
      specs[i] = {spec[1], (right - left) / 100}
      left = right
    else
      specs[i] = {spec[1], weights[i] / total}
    end
  end
  block.colspecs = specs
end

local function flush(out, run)
  if #run == 0 then return end
  local short = #run <= 2 and #pandoc.utils.stringify(run) <= 365
  for _, block in ipairs(run) do short = short and block.t == "Para" end
  short = short or (#run == 1 and keeps_list(run[1]))
  if short then
    table.insert(out, latex("\\begin{FolioNarrowProse}"))
    for _, block in ipairs(run) do table.insert(out, block) end
    table.insert(out, latex("\\end{FolioNarrowProse}"))
  else
    table.insert(out, pandoc.Div(run, pandoc.Attr("", {"reading-columns"})))
  end
end

function Pandoc(doc)
  local out, run = {}, {}
  local column_math = doc.meta["folio-column-math"] == true
  for i, block in ipairs(doc.blocks) do
    local subheading = block.t == "Header" and block.level > 1
    if prose(block, column_math) or (subheading and prose(doc.blocks[i + 1], column_math)) then
      table.insert(run, block)
    else
      flush(out, run)
      run = {}
      if block.t == "Table" then span_table(block) end
      local inline = figure(block)
      if inline then table.insert(out, latex("\\begin{FolioInlineFigure}")) end
      table.insert(out, block)
      if inline then table.insert(out, latex("\\end{FolioInlineFigure}")) end
    end
  end
  flush(out, run)
  doc.blocks = out
  return doc
end
