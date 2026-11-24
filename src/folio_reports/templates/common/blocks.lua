-- Keep the contents as Pandoc blocks so emphasis, links and footnotes survive.
function Div(block)
  if not block.classes:includes("metric") then return nil end
  local value = block.attributes.value
  if not value or value == "" then error("A metric needs a value attribute.") end
  local body = {pandoc.Plain({
    pandoc.RawInline("latex", "\\begin{FolioMetric}{"),
    pandoc.Str(value),
    pandoc.RawInline("latex", "}"),
  })}
  for _, paragraph in ipairs(block.content) do table.insert(body, paragraph) end
  table.insert(body, pandoc.RawBlock("latex", "\\end{FolioMetric}"))
  return body
end
