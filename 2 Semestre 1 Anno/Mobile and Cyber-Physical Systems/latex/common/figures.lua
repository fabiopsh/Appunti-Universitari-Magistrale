-- figures.lua
-- I paragrafi che iniziano con un'immagine seguita (stessa riga/paragrafo) da
-- testo di didascalia vengono convertiti in una vera figure centrata, con il
-- testo come \caption sotto l'immagine.
--
-- Le immagini "da sole" sono gia' Figure implicite (centrate) in pandoc 3.x:
-- questo filtro non le tocca. Le immagini inline in mezzo al testo restano inline.

local function is_break(inl)
  return inl.t == 'SoftBreak' or inl.t == 'LineBreak' or inl.t == 'Space'
end

local function trim(inls)
  while #inls > 0 and is_break(inls[1]) do table.remove(inls, 1) end
  while #inls > 0 and is_break(inls[#inls]) do table.remove(inls) end
  return inls
end

function Para(el)
  local c = el.content
  if #c == 0 or c[1].t ~= 'Image' then
    return nil
  end
  local img = c[1]

  -- inline DOPO l'immagine = didascalia
  local rest = {}
  for i = 2, #c do rest[#rest + 1] = c[i] end
  rest = trim(rest)

  -- nessuna didascalia attaccata -> lascia stare (inline o gia' figure)
  if #rest == 0 then
    return nil
  end

  -- se la didascalia e' tutta dentro un singolo *...* (Emph), togli il wrapper:
  -- ci pensa \captionsetup{textfont=it} a renderla in corsivo
  if #rest == 1 and rest[1].t == 'Emph' then
    rest = trim(pandoc.List(rest[1].content):map(function(x) return x end))
  end

  -- togli un prefisso etichetta tipo "Fig." / "Figura" e un eventuale dash/":"
  if #rest > 0 and rest[1].t == 'Str' and rest[1].text:match('^[Ff]ig%a*%.?$') then
    table.remove(rest, 1)
    rest = trim(rest)
    if #rest > 0 and rest[1].t == 'Str' and rest[1].text:match('^[—–%-:]+$') then
      table.remove(rest, 1)
      rest = trim(rest)
    end
  end

  if #rest == 0 then
    return nil
  end

  -- l'alt dell'immagine non deve diventare didascalia
  img.caption = pandoc.Inlines({})

  local caption = pandoc.Caption(pandoc.Blocks({ pandoc.Plain(pandoc.Inlines(rest)) }))
  return pandoc.Figure(pandoc.Blocks({ pandoc.Plain({ img }) }), caption)
end
