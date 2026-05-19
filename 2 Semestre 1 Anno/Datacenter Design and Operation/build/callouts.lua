-- Pandoc Lua filter: Obsidian callouts -> LaTeX tcolorbox
-- Detects BlockQuote starting with "[!type] Optional title" and converts to a styled box.
-- Handles both spacings:
--   > [!type] Title         > [!type] Title
--   >                       > body line
--   > body line

local TYPES = {
  note       = "calloutnote",
  info       = "calloutnote",
  abstract   = "calloutnote",
  summary    = "calloutnote",
  tip        = "callouttip",
  example    = "callouttip",
  warning    = "calloutwarning",
  danger     = "calloutimportant",
  important  = "calloutimportant",
  question   = "calloutquestion",
  definition = "calloutdefinition",
  theorem    = "callouttheorem",
}

local function escape_latex(s)
  return (s:gsub("([\\#%${}&_%%~])", "\\%1"))
end

local function strip_space_inlines(inlines)
  while #inlines > 0 and (inlines[1].t == "Space" or inlines[1].t == "SoftBreak" or inlines[1].t == "LineBreak") do
    table.remove(inlines, 1)
  end
  while #inlines > 0 and (inlines[#inlines].t == "Space" or inlines[#inlines].t == "SoftBreak" or inlines[#inlines].t == "LineBreak") do
    table.remove(inlines)
  end
end

function BlockQuote(el)
  if #el.content == 0 then return nil end
  local first = el.content[1]
  if first.t ~= "Para" and first.t ~= "Plain" then return nil end
  if #first.content == 0 then return nil end

  -- The first inline should be Str like "[!type]"
  local marker = pandoc.utils.stringify(first.content[1])
  local ctype = marker:match("^%[!(%w+)%]$")
  if not ctype then
    -- Fallback: match across stringified prefix in case it's split into pieces
    local prefix = pandoc.utils.stringify(first):sub(1, 32)
    ctype = prefix:match("^%[!(%w+)%]")
    if not ctype then return nil end
  end
  ctype = ctype:lower()
  local env = TYPES[ctype] or "calloutnote"

  -- Split first paragraph inlines into title and inline-body at first SoftBreak/LineBreak
  local inlines = first.content
  local break_idx = nil
  for i, inl in ipairs(inlines) do
    if inl.t == "SoftBreak" or inl.t == "LineBreak" then
      break_idx = i
      break
    end
  end

  local title_inlines, body_inlines
  if break_idx then
    title_inlines = {}
    for i = 1, break_idx - 1 do title_inlines[#title_inlines + 1] = inlines[i] end
    body_inlines = {}
    for i = break_idx + 1, #inlines do body_inlines[#body_inlines + 1] = inlines[i] end
  else
    title_inlines = {}
    for i = 1, #inlines do title_inlines[i] = inlines[i] end
    body_inlines = {}
  end

  -- Drop the leading "[!type]" Str (first element of title_inlines)
  if #title_inlines > 0 then
    table.remove(title_inlines, 1)
  end
  strip_space_inlines(title_inlines)
  strip_space_inlines(body_inlines)

  local title_str = pandoc.utils.stringify(title_inlines)
  title_str = title_str:gsub("^%s+", ""):gsub("%s+$", "")

  local out = {}
  out[#out + 1] = pandoc.RawBlock("latex", "\\begin{" .. env .. "}{" .. escape_latex(title_str) .. "}")
  if #body_inlines > 0 then
    out[#out + 1] = pandoc.Para(body_inlines)
  end
  for i = 2, #el.content do
    out[#out + 1] = el.content[i]
  end
  out[#out + 1] = pandoc.RawBlock("latex", "\\end{" .. env .. "}")
  return out
end
