;;Copyright (C) 2008-2013 Muthiah Annamalai

(setq ezhil-keywords '("ஆனால்" "ஏதேனில்" "தேர்வு" "பதிப்பி" "தேர்ந்தெடு" "இல்லைஆனால்" "பதிப்பி" "ஆக" "இல்லை" "வரை" "செய்" "பின்கொடு" "முடி" "நிரல்பாகம்" "தொடர்" "நேருத்து") )
(setq ezhil-types '("float" "int" "string"))
(setq ezhil-constants '("None" "True" "False"))
(setq ezhil-events '())
(setq ezhil-functions '("abs" "acos" "len" "assert" "seed" "exit" "randint" "choice" "random"))

;; create the regex string for each class of keywords
(setq ezhil-keywords-regexp (regexp-opt ezhil-keywords 'words))
(setq ezhil-type-regexp (regexp-opt ezhil-types 'words))
(setq ezhil-constant-regexp (regexp-opt ezhil-constants 'words))
(setq ezhil-event-regexp (regexp-opt ezhil-events 'words))
(setq ezhil-functions-regexp (regexp-opt ezhil-functions 'words))

;; clear memory
(setq ezhil-keywords nil)
(setq ezhil-types nil)
(setq ezhil-constants nil)
(setq ezhil-events nil)
(setq ezhil-functions nil)

;; create the list for font-lock.
;; each class of keyword is given a particular face
(setq ezhil-font-lock-keywords
  `(
    (,ezhil-type-regexp . font-lock-type-face)
    (,ezhil-constant-regexp . font-lock-constant-face)
    (,ezhil-event-regexp . font-lock-builtin-face)
    (,ezhil-functions-regexp . font-lock-function-name-face)
    (,ezhil-keywords-regexp . font-lock-keyword-face)
    ;; note: order above matters. “ezhil-keywords-regexp” goes last because
    ;; otherwise the keyword “state” in the function “state_entry”
    ;; would be highlighted.
))

;; define the mode
(define-derived-mode ezhil-mode fundamental-mode
  "ezhil-lang mode"
  "Major mode for editing ezhil (Ezhil-Lang : Write imperative programs in Indian language Tamil …"

  ;; code for syntax highlighting
  (setq font-lock-defaults '((ezhil-font-lock-keywords)))

  ;; clear memory
  (setq ezhil-keywords-regexp nil)
  (setq ezhil-types-regexp nil)
  (setq ezhil-constants-regexp nil)
  (setq ezhil-events-regexp nil)
  (setq ezhil-functions-regexp nil)
)

(provide 'ezhil-mode)
