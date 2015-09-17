// vim: set ts=4 sw=4 expandtab
// (C) 2010 Dan Bravender - licensed under the AGPL 3.0

/*  Geulja is used to track modifications that have been made to
    characters. Currently, it keeps track of characters' original
    padchims (for \u3137 -> \u3139 irregulars) and if the character has
    no padchim but should be treated as if it does (for \u3145
    irregulars). When substrings are extracted the Geulja class
    keeps these markers for the last character only.
*/

// Code taken from https://github.com/dbravender/korean_conjugation/tree/master/html

function Geulja(__value__) {
    this.length = (this.__value__ = __value__ || "").length;
    this.hidden_padchim = false;
    this.original_padchim = null;
    this.charAt = function() {
        result = String.prototype.charAt.apply(this, arguments);
        if (arguments[0] == this.length - 1) {
            result = new Geulja(result);
            result.original_padchim = this.original_padchim;
            result.hidden_padchim = this.hidden_padchim;
        }
        return result;
    }
};

Geulja.prototype.toString = function() {
    return this.__value__;
}

Geulja.prototype.valueOf = function() {
    return this.__value__;
}

var hangeul = function() {
    this.Geulja = Geulja;
    this.is_hangeul = function(character) {
        if (character.charCodeAt(0) >= 44032 &&
            character.charCodeAt(0) <= 55203) {
            return true;
        }
        return false;
    };
    this.is_hangeul_string = function(string) {
        return string
               // remove spaces and punctuation
               .replace(/[!"\?\. ]/g, '')
               .split('')
               .every(this.is_hangeul);
    }
    // Equations lifted directly from:
    // http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html
    this.lead = function(character) {
        return String.fromCharCode((Math.floor(character.charCodeAt(0) - 44032) / 588) + 4352);
    };
    this.vowel = function(character) {
        padchim_character = this.padchim(character);
        if (!padchim_character || padchim_character == true) {
            padchim_offset = -1;
        } else {
            padchim_offset = padchim_character.charCodeAt(0) - 4520;
        }
        return String.fromCharCode(Math.floor(((character.charCodeAt(0) - 44032 - padchim_offset) % 588) / 28) + 12623);
    };
    this.padchim = function(character) {
        if (character.hidden_padchim) {
            return true;
        }
        if (character.original_padchim) {
            return character.original_padchim;
        }
        p = String.fromCharCode(((character.charCodeAt(0) - 44032) % 28) + 4520 - 1)
        if (p.charCodeAt(0) == 4519) {
            return null;
        } else {
            return p;
        }
    };
    this.join = function(lead, vowel, padchim) {
        lead_offset = lead.charCodeAt(0) - 4352;
        vowel_offset = vowel.charCodeAt(0) - 12623;
        if (padchim) {
            padchim_offset = padchim.charCodeAt(0) - 4520;
        } else {
            padchim_offset = -1;
        }
        return String.fromCharCode(padchim_offset + (vowel_offset) * 28 + (lead_offset) * 588 + 44032 + 1);
    };
    this.split = function(geulja) {
        return [lead(geulja), vowel(geulja), padchim(geulja)];
    };
    this.spread = function(string) {
        return string
               .split('')
               .map(this.split)
               .reduce(function(a, b) { return a.concat(b) })
               .join('');
    };
    this.find_vowel_to_append = function(string) {
        self = this;
        append = null;
        for (character in string.split('').reverse()) {
            if (character in {'\uB728': true, '\uC4F0': true, '\uD2B8': true}) {
                if (!append) append = '\uC5B4';
            }
            if (self.vowel(character) == '\u3161' && !self.padchim(character)) {
                //continue
            } else if (self.vowel(character) in {'\u3157': true, '\u314F': true, '\u3151': true}) {
                if (!append) append = '\uC544';
            } else {
                if (!append) append = '\uC5B4';
            }
        }
        if (!append) append = '\uC5B4';
        return append;
    };
    this.match = function(character, l, v, p) {
        return (l == '*' || this.lead(character) == l) &&
               (v == '*' || this.vowel(character) == v) &&
               (p == '*' || this.padchim(character) == p)
    };
    return this;
}();

var pronunciation = {};


pronunciation.padchim_to_lead = {
    '\u11A8': '\u1100',
    '\u11A9': '\u1101',
    '\u11AB': '\u1102',
    '\u11AE': '\u1103',
    '\u11AF': '\u1105',
    '\u11B7': '\u1106',
    '\u11B8': '\u1107',
    '\u11BA': '\u1109',
    '\u11BB': '\u110A',
    '\u11BC': '\u110B',
    '\u11BD': '\u110C',
    '\u11BE': '\u110E',
    '\u11BF': '\u110F',
    '\u11C0': '\u1110',
    '\u11C1': '\u1111',
    '\u11C2': '\u1112'
};

pronunciation.move_padchim_to_replace_eung = function(x, y) {
    if (hangeul.padchim(x[x.length-1]) == '\u11BC') {
        return;
    }
    if (hangeul.padchim(x[x.length-1]) in pronunciation.padchim_to_lead &&
        hangeul.lead(y[0]) == '\u110B') {
        return [x.substring(0, x.length-1) + hangeul.join(hangeul.lead(x[x.length-1]),
                                                          hangeul.vowel(x[x.length-1])),
                hangeul.join(pronunciation.padchim_to_lead[hangeul.padchim(x[x.length-1])],
                             hangeul.vowel(y[0]),
                             hangeul.padchim(y[0])) +
                y.substring(1)];
    }
};

pronunciation.change_padchim_pronunciation = function(to, changers) {
    return function(x, y) {
        if (hangeul.padchim(x[x.length-1]) in changers) {
            return [x.substring(0, x.length-1) +
                    hangeul.join(hangeul.lead(x[x.length-1]),
                                 hangeul.vowel(x[x.length-1]),
                                 to),
                    y];
        }
    }
};

pronunciation.consonant_combination_rule = function(x_padchim, y_lead, new_padchim,
                                                    new_lead, y_vowel) {
    return function(x, y) {
        if (y_vowel && hangeul.vowel(y[0]) != y_vowel) {
            return;
        }
        if ((hangeul.padchim(x[x.length-1]) == x_padchim || x_padchim == '*') &&
            (hangeul.lead(y[0]) == y_lead || y_lead == '*')) {
            return [x.substring(0, x.length-1) +
                    hangeul.join(hangeul.lead(x[x.length-1]),
                                 hangeul.vowel(x[x.length-1]),
                                 new_padchim == '*' ? hangeul.padchim(x[-1]) : new_padchim),
                    hangeul.join(new_lead == '*' ? hangeul.lead(y[0]) : new_lead,
                                 hangeul.vowel(y[0]),
                                 hangeul.padchim(y[0])) +
                    y.substring(1)];
        }
    }
};

pronunciation.skip_non_hangeul = function(x, y) {
    if (!hangeul.is_hangeul(x[x.length-1])) {
        return [x, y, true];
    }
};

pronunciation.merge_rules = [
/* WARNING: Please be careful when adding/modifying rules since padchim 
            hangeul.and lead characters are different Unicode characters. Please see:
            http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html
   Rules from http://en.wikibooks.org/wiki/Korean/Advanced_Pronunciation_Rules
*/
    pronunciation.skip_non_hangeul,
    pronunciation.consonant_combination_rule('\u11C2', '\u110B', null, '\u110B', null),
    // \u3131\u3134 becomes \u3147\u3134
    pronunciation.consonant_combination_rule('\u11A8', '\u1102', '\u11BC', '\u1102', null),
    // \u3131\u3141 becomes \u3147\u3141
    pronunciation.consonant_combination_rule('\u11A8', '\u1106', '\u11BC', '\u1106', null),
    // \u314B\u3134 becomes \u3147\u3134
    pronunciation.consonant_combination_rule('\u11BF', '\u1102', '\u11BC', '\u1102', null),
    // \u314B\u3141 becomes \u3147\u3141
    pronunciation.consonant_combination_rule('\u11BF', '\u1106', '\u11BC', '\u1106', null),
    // \u3137\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11AE', '\u1102', '\u11AB', '\u1102', null),
    // \u3137\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11AE', '\u1106', '\u11AB', '\u1106', null),
    // \u3145\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11BA', '\u1102', '\u11AB', '\u1102', null),
    // \u3146\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11BB', '\u1102', '\u11AB', '\u1102', null),
    // \u3145\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11BA', '\u1106', '\u11AB', '\u1106', null),
    // \u3131 \u3146 becomes \u3131 \u3146
    pronunciation.consonant_combination_rule('\u11A8', '\u1109', '\u11A8', '\u110A', null),
    // \u3148\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11BD', '\u1102', '\u11AB', '\u1102', null),
    // \u3148\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11BD', '\u1106', '\u11AB', '\u1106', null),
    // \u314A\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11BE', '\u1102', '\u11AB', '\u1102', null),
    // \u314A\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11BE', '\u1106', '\u11AB', '\u1106', null),
    // \u314C\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11C0', '\u1102', '\u11AB', '\u1102', null),
    // \u314C\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11C0', '\u1106', '\u11AB', '\u1106', null),
    //  \u314E\u3134 becomes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11C2', '\u1102', '\u11AB', '\u1102', null),
    //  \u314E\u3141 becomes \u3134\u3141
    pronunciation.consonant_combination_rule('\u11C2', '\u1106', '\u11AB', '\u1106', null),
    //  \u3142\u3134 becomes \u3141\u3134
    pronunciation.consonant_combination_rule('\u11B8', '\u1102', '\u11B7', '\u1102', null),
    // \u3142\u3141 becomes \u3141\u3141
    pronunciation.consonant_combination_rule('\u11B8', '\u1106', '\u11B7', '\u1106', null),
    // \u314D\u3134 becomes \u3141\u3134
    pronunciation.consonant_combination_rule('\u11C1', '\u1102', '\u11B7', '\u1102', null),
    // \u314D\u3141 becomes \u3141\u3141
    pronunciation.consonant_combination_rule('\u11C1', '\u1106', '\u11B7', '\u1106', null),
    //  \u3131\u314E becomes \u314B
    pronunciation.consonant_combination_rule('\u11A8', '\u1112', null, '\u110F', null),
    //  \u314E\u3131 becomes \u314B
    pronunciation.consonant_combination_rule('\u11C2', '\u1100', null, '\u110F', null),
    // \u314E\u3137 becomes \u314C
    pronunciation.consonant_combination_rule('\u11C2', '\u1103', null, '\u1110', null),
    // \u3137\u314E becomes \u314C
    pronunciation.consonant_combination_rule('\u11AE', '\u1112', null, '\u1110', null),
    // \u3142\u314E becomes \u314D
    pronunciation.consonant_combination_rule('\u11B8', '\u1112', null, '\u1111', null),
    // \u314E\u3142 becomes \u314D
    pronunciation.consonant_combination_rule('\u11C2', '\u1107', null, '\u1111', null),
    // \u3148\u314E becomes \u314A
    pronunciation.consonant_combination_rule('\u11BD', '\u1112', null, '\u110E', null),
    // \u314E\u3148 becomes \u314A
    pronunciation.consonant_combination_rule('\u11C2', '\u110C', null, '\u110E', null),
    // \u314E\u3145 becomes \u3146
    pronunciation.consonant_combination_rule('\u11C2', '\u1109', null, '\u110A', null),
    //\u3137\uC774 becomes \uC9C0
    pronunciation.consonant_combination_rule('\u11AE', '\u110B', null, '\u110C', '\u3163'),
    //\u314C\uC774 becomes \uCE58
    pronunciation.consonant_combination_rule('\u11C0', '\u110B', null, '\u110E', '\u3163'),
    //\u3131\u3139 becomes \u3147\u3134
    pronunciation.consonant_combination_rule('\u11A8', '\u1105', '\u11BC', '\u1102', null),
    //\u3134\u3139 becomes \u3139\u3139 // TODO: (not sure how to fix pronunciation) also sometimes \u3134\u3134
    pronunciation.consonant_combination_rule('\u11AB', '\u1105', '\u11AF', '\u1105', null),
    // \u3141\u3139 becomes \u3141\u3134
    pronunciation.consonant_combination_rule('\u11B7', '\u1105', '\u11B7', '\u1102', null),
    // \u3147\u3139 becomes \u3147\u3134
    pronunciation.consonant_combination_rule('\u11BC', '\u1105', '\u11BC', '\u1102', null),
    // \u3142\u3139 becomes \u3141\u3134
    pronunciation.consonant_combination_rule('\u11B8', '\u1105', '\u11B7', '\u1102', null),
    // \u3145 \u314E becomes \u314C
    pronunciation.consonant_combination_rule('\u11BA', '\u1112', null, '\u1110', null),
    // \uBC1B\uCE68 followed by \u3147: replace \u3147 with \uBC1B\uCE68 (use second \uBC1B\uCE68 if there are two). Otherwise, \uBC1B\uCE68 followed by consonant:
    pronunciation.move_padchim_to_replace_eung,
    //    * \u3131, \u314B: like \u3131
    //    * \u3137, \u3145, \u3148, \u314A, \u314C, \u314E: like \u3137
    //    * \u3142, \u314D: like \u3142
    // Double padchim rules
    pronunciation.consonant_combination_rule('\u11B1', '\u110B', '\u11AF', '\u1106', null),
    pronunciation.consonant_combination_rule('\u11B9', '\u110B', '\u11B8', '\u1109', null),
    pronunciation.consonant_combination_rule('\u11B1', '*', '\u11B7', '*', null),
    pronunciation.consonant_combination_rule('\u11B6', '\u110B', null, '\u1105', null),
    pronunciation.consonant_combination_rule('\u11B6', '*', '\u11AF', '*', null),
    pronunciation.consonant_combination_rule('\u11AC', '\u110B', '\u11AB', '\u110C', null),
    pronunciation.consonant_combination_rule('\u11AC', '*', '\u11AB', '*', null),
    // \uD559\uAD50 -> \uD559\uAF9C
    pronunciation.consonant_combination_rule('\u11A8', '\u1100', '\u11A8', '\u1101', null),
    // \uBC25\uC1A5-> \uBC25\uC3DF
    pronunciation.consonant_combination_rule('\u11B8', '\u1109', '\u11B8', '\u110A', null),
    // \uC788\uC2B5\uB2C8\uB2E4 -> \uC774\uC500\uB2C8\uB2E4
    pronunciation.consonant_combination_rule('\u11BB', '\u1109', null, '\u110A', null),
    pronunciation.change_padchim_pronunciation('\u11AE', {'\u11BA': true, '\u11BB': true, '\u11BD': true, '\u11BE': true, '\u11C0': true, '\u11C2': true}),
    pronunciation.change_padchim_pronunciation('\u11B8', {'\u11C1': true}),
    pronunciation.consonant_combination_rule('\u11AE', '\u1103', null, '\u1104'),
    function (x, y) { return [x, y] }
];

pronunciation.apply_rules = function(x, y) {
    result = null;
    for (rule in pronunciation.merge_rules) {
        merge = rule(x, y);
        if (merge && merge.length == 3) {
            x = merge[0];
            y = merge[1];
            stop = merge[2];
            if (stop) {
                result = x + y;
            }
        } else if (merge) {
            x = merge[0];
            y = merge[1];
        }
    };
    if (result) {
        return result;
    }
    return x + y;
};

pronunciation.get_pronunciation = function(word) {
    return (word + String.fromCharCode(0)).split('').reduce(pronunciation.apply_rules).substring(0, word.length);
};

// This will be incremented when the algorithm is modified so clients
// that have cached API calls will know that their cache is invalid
pronunciation.version = 1;

var conjugator = {};

conjugator.no_padchim_rule = function(characters) {
    /* no_padchim_rule is a helper function for defining merges where a
        character will take the padchim of a merged character if the first
        character doesn't already have a padchim, .e.g. \uC2B5 -> \uAC00 + \uC2B5\uB2C8\uB2E4 -> \uAC11\uB2C8\uB2E4.
    */
    return function(x, y) {
        if (!hangeul.padchim(x.charAt(x.length-1)) && y[0] in characters) {
            return ['borrow padchim', x.substring(0, x.length-1) +
                                      hangeul.join(hangeul.lead(x[x.length-1]),
                                                   hangeul.vowel(x[x.length-1]),
                                                   hangeul.padchim(y[0])) +
                                      y.substring(1)];
        }
    }
};

conjugator.vowel_contraction = function(vowel1, vowel2, new_vowel, trace) {
    /* vowel contraction is a helper function for defining common contractions
       between a character without a padchim and a character that starts with
        '\u110B', e.g. \u3150 + \u3155 -> \u3150 when applied to \uD574 + \uC600 yields \uD588.
    */
    return function(x, y) {
        if (hangeul.match(x.charAt(x.length-1), '*', vowel1, null) &&
            hangeul.match(y.charAt(0), '\u110B', vowel2, '*')) {
            return ['vowel contraction [' + vowel1 + ' ' + vowel2 + ' -> ' + new_vowel + ']',
                    x.substring(0, x.length-1) +
                    hangeul.join(hangeul.lead(x.charAt(x.length-1)),
                                 new_vowel,
                                 hangeul.padchim(y[0])) +
                    y.substring(1)];
        }
    }
};

conjugator.drop_l = function(x, y) {
    if (hangeul.padchim(x[x.length-1]) == '\u11AF') {
        conjugator.reasons.push('drop \u3139')
        return x.substring(0, x.length-1) +
               hangeul.join(hangeul.lead(x[x.length-1]),
                            hangeul.vowel(x[x.length-1])) +
               y;
    }
};

conjugator.drop_l_and_borrow_padchim = function(x, y) {
    if (hangeul.padchim(x.charAt(x.length-1)) == '\u11AF') {
        conjugator.reasons.push('drop ' + hangeul.padchim(x.charAt(x.length-1)) + ' borrow padchim')
        return x.substring(0, x.length-1) +
               hangeul.join(hangeul.lead(x[x.length-1]),
                            hangeul.vowel(x[x.length-1]),
                            hangeul.padchim(y[0])) +
               y.substring(1);
    }
};

conjugator.dont_insert_eh = function(x, y) {
    if (hangeul.padchim(x.charAt(x.length-1)) == '\u11AF' &&
        y[0] == '\uBA74') {
        return ['join', x + y];
    }
};

conjugator.insert_eh = function(characters) {
    return function(x, y) {
        if (hangeul.padchim(x.charAt(x.length-1)) && y[0] in characters) {
            return ['padchim + consonant -> insert \uC73C', x + '\uC73C' + y];
        }
    }
};

conjugator.lm_merge = function(x, y) {
    if (hangeul.padchim(x.charAt(x.length-1)) == '\u11AF' && y[0] == '\uC74C') {
        return ['\u3139 + \u3141 -> \u11B1',
                x.substring(0, x.length-1) +
                hangeul.join(hangeul.lead(x[x.length-1]),
                             hangeul.vowel(x[x.length-1]),
                             '\u11B1')];
    }
};

/* merge rules is a list of rules that are applied in order when merging a verb 
   stem with a tense ending
*/

conjugator.merge_rules = [
    conjugator.no_padchim_rule({'\uC744': true, '\uC2B5': true, '\uC74D': true, '\uB294': true, '\uC74C': true}),
    conjugator.lm_merge,
    conjugator.vowel_contraction('\u3150', '\u3153', '\u3150'),
    conjugator.vowel_contraction('\u3161', '\u3153', '\u3153'),
    conjugator.vowel_contraction('\u315C', '\u3153', '\u315D'),
    conjugator.vowel_contraction('\u3157', '\u314F', '\u3158'),
    conjugator.vowel_contraction('\u315A', '\u3153', '\u3159'),
    conjugator.vowel_contraction('\u3159', '\u3153', '\u3159'),
    conjugator.vowel_contraction('\u3158', '\u3153', '\u3158'),
    conjugator.vowel_contraction('\u315D', '\u3153', '\u315D'),
    conjugator.vowel_contraction('\u314F', '\u314F', '\u314F'),
    conjugator.vowel_contraction('\u3161', '\u314F', '\u314F'),
    conjugator.vowel_contraction('\u3163', '\u3153', '\u3155'),
    conjugator.vowel_contraction('\u3153', '\u3153', '\u3153'),
    conjugator.vowel_contraction('\u3153', '\u3163', '\u3150'),
    conjugator.vowel_contraction('\u314F', '\u3163', '\u3150'),
    conjugator.vowel_contraction('\u3151', '\u3163', '\u3152'),
    conjugator.vowel_contraction('\u3152', '\u3153', '\u3152'),
    conjugator.vowel_contraction('\u3154', '\u3153', '\u3154'),
    conjugator.vowel_contraction('\u3155', '\u3153', '\u3155'),
    conjugator.vowel_contraction('\u314F', '\u3155', '\u3150'),
    conjugator.vowel_contraction('\u3156', '\u3153', '\u3156'),
    conjugator.vowel_contraction('\u315E', '\u3153', '\u315E'),
    conjugator.dont_insert_eh,
    conjugator.insert_eh({'\uBA74': true, '\uC138': true, '\uC2ED': true}),
    // default rule
    function (x, y) {
        return ['join', x + y];
    }
];

conjugator.reasons = [];

conjugator.merge = function(x, y) {
    /* concatenates every element in a list using the rules to
       merge the strings
    */
    var response = null;
    conjugator.merge_rules.forEach(function(rule) {
        if (!response) {
            output = rule(x, y);
            if (output) {
                conjugator.reasons.push((output[0] ? output[0] : '') + ' (' + x + ' + ' + y + ' -> ' + output[1] + ')');
                response = output[1];
            }
        }
    });
    return response;
};

conjugator.both_regular_and_irregular = {
    '\uC77C': true, '\uACF1': true, '\uD30C\uBB3B': true, '\uB204\uB974': true, '\uBB3B': true, '\uC774\uB974': true,
    '\uB418\uBB3B': true, '\uC370': true, '\uBD93': true, '\uB4E4\uAE4C\uBD88': true, '\uAD7D': true, '\uAC77': true,
    '\uB4A4\uAE4C\uBD88': true, '\uAE4C\uBD88': true
};

conjugator.regular_ees = {
    '\uAC00\uB824\uBCF4\uC774': true, '\uAC00\uB85C\uB193\uC774': true, '\uAC00\uB85C\uB204\uC774': true, '\uAC00\uB85C\uCC44\uC774': true, '\uAC00\uB9AC\uC774': true, '\uAC04\uC885\uC774': true,
    '\uAC08\uB77C\uBD99\uC774': true, '\uAC08\uB9C8\uB4E4\uC774': true, '\uAC08\uBD99\uC774': true, '\uAC08\uC544\uB4E4\uC774': true, '\uAC08\uC544\uBD99\uC774': true, '\uAC10\uC2F8\uC774': true,
    '\uAC38\uC6B8\uC774': true, '\uAC70\uB450\uC5B4\uB4E4\uC774': true, '\uAC70\uB46C\uB4E4\uC774': true, '\uAC70\uBA38\uB4E4\uC774': true, '\uAC74\uB108\uB2E4\uBCF4\uC774': true,
    '\uAC74\uC911\uC774': true, '\uAC77\uC5B4\uBD99\uC774': true, '\uAC78\uBA38\uBA54\uC774': true, '\uAC78\uBA54\uC774': true, '\uAC78\uCC44\uC774': true, '\uAC78\uD130\uB4E4\uC774': true,
    '\uAC89\uB728\uC774': true, '\uAC89\uC808\uC774': true, '\uACB9\uC313\uC774': true, '\uACC1\uB4E4\uC774': true, '\uACC1\uBD99\uC774': true, '\uACE0\uC774': true, '\uACE0\uC774': true,
    '\uACE4\uB450\uBC15\uC774': true, '\uACF1\uAEBE\uC774': true, '\uACF1\uB193\uC774': true, '\uACF1\uB4E4\uC774': true, '\uACF1\uBA39\uC774': true, '\uACF5\uB4E4\uC774': true,
    '\uAD34\uC774': true, '\uAD34\uC774': true, '\uAD7D\uC5B4\uBCF4\uC774': true, '\uAD7D\uC8C4\uC774': true, '\uADF8\uB7EC\uB4E4\uC774': true, '\uAE30\uC6B8\uC774': true,
    '\uAE30\uC774': true, '\uAE30\uC8FD\uC774': true, '\uAE38\uB4E4\uC774': true, '\uAE43\uB4E4\uC774': true, '\uAE4A\uC774': true, '\uAE4C\uBD99\uC774': true, '\uAE4C\uC774': true,
    '\uAE4E\uC774': true, '\uAE4E\uC774': true, '\uAE54\uBCF4\uC774': true, '\uAE68\uC774': true, '\uAE84\uC6B8\uC774': true, '\uAEBC\uB4E4\uC774': true, '\uAEBE\uC774': true,
    '\uAF2C\uC774': true, '\uAF2C\uC774': true, '\uAF2C\uC774': true, '\uAF2C\uC774': true, '\uAF3D\uB4E4\uC774': true, '\uAF80\uC774': true, '\uAFB8\uC774': true,
    '\uAFB8\uC774': true, '\uAFF0\uC774': true, '\uB044\uC219\uC774': true, '\uB044\uC9D1\uC5B4\uB4E4\uC774': true, '\uB04A\uC774': true, '\uB04C\uC5B4\uB4E4\uC774': true,
    '\uB053\uC774': true, '\uB07C\uC6B8\uC774': true, '\uB07C\uC774': true, '\uB07C\uC774': true, '\uB098\uB204\uC774': true, '\uB098\uB364\uBC99\uC774': true,
    '\uB098\uBC88\uB4DD\uC774': true, '\uB09A\uC774': true, '\uB0AE\uBCF4\uC774': true, '\uB0B4\uB193\uC774': true, '\uB0B4\uB2E4\uBCF4\uC774': true, '\uB0B4\uB824\uB2E4\uBCF4\uC774': true,
    '\uB0B4\uB824\uBD99\uC774': true, '\uB0B4\uB9AC\uB36E\uC774': true, '\uB0B4\uB9AC\uBA39\uC774': true, '\uB0B4\uB9AC\uC313\uC774': true, '\uB0B4\uB9AC\uCABC\uC774': true,
    '\uB0B4\uBCF4\uC774': true, '\uB0B4\uBCF4\uC774': true, '\uB0B4\uBD99\uC774': true, '\uB118\uACA8\uB2E4\uBCF4\uC774': true, '\uB118\uBCF4\uC774': true, '\uB178\uB290\uC774': true,
    '\uB179\uC774': true, '\uB192\uC774': true, '\uB193\uC544\uBA39\uC774': true, '\uB193\uC774': true, '\uB204\uC774': true, '\uB204\uC774': true, '\uB204\uC774': true,
    '\uB204\uC774': true, '\uB204\uC774': true, '\uB205\uC774': true, '\uB208\uAE30\uC774': true, '\uB298\uC774': true, '\uB298\uC774': true, '\uB298\uC904\uC774': true,
    '\uB2E4\uAC00\uBD99\uC774': true, '\uB2E4\uBD99\uC774': true, '\uB2E6\uC774': true, '\uB2E6\uC774': true, '\uB2EC\uC774': true, '\uB2F5\uC313\uC774': true,
    '\uB367\uB07C\uC774': true, '\uB367\uB193\uC774': true, '\uB367\uB36E\uC774': true, '\uB367\uB4E4\uC774': true, '\uB367\uB4E4\uC774': true, '\uB367\uBCF4\uC774': true,
    '\uB367\uBD99\uC774': true, '\uB367\uC313\uC774': true, '\uB36E\uC2F8\uC774': true, '\uB36E\uC313\uC774': true, '\uB36E\uC774': true, '\uB370\uAC85\uC774': true,
    '\uB3C4\uB450\uBCF4\uC774': true, '\uB3CB\uBCF4\uC774': true, '\uB3CC\uB824\uB2E4\uBD99\uC774': true, '\uB3D9\uC774': true, '\uB418\uBC15\uC774': true, '\uB418\uC4F0\uC774': true,
    '\uB418\uCE58\uC774': true, '\uB458\uB7EC\uC2F8\uC774': true, '\uB4A4\uAF2C\uC774': true, '\uB4A4\uB193\uC774': true, '\uB4A4\uB36E\uC774': true, '\uB4A4\uBC14\uAFB8\uC774': true,
    '\uB4A4\uBC29\uC774': true, '\uB4A4\uBCF6\uC774': true, '\uB4A4\uC11E\uC774': true, '\uB4A4\uC5CE\uC774': true, '\uB4DC\uB192\uC774': true, '\uB4DC\uB7EC\uC313\uC774': true,
    '\uB4DC\uB7EC\uC7A5\uC774': true, '\uB4E4\uB728\uC774': true, '\uB4E4\uBCF6\uC774': true, '\uB4E4\uC5EC\uB2E4\uBCF4\uC774': true, '\uB4E4\uC774\uB07C\uC774': true,
    '\uB4E4\uC774\uB07C\uC774': true, '\uB4E4\uC774': true, '\uB4E4\uC774': true, '\uB4E4\uC774\uC313\uC774': true, '\uB4E4\uC774\uC313\uC774': true, '\uB54B\uC774': true,
    '\uB54C\uB824\uB204\uC774': true, '\uB54C\uB824\uC8FD\uC774': true, '\uB5A0\uBA39\uC774': true, '\uB5A0\uBC8C\uC774': true, '\uB5A0\uC774': true, '\uB5BC\uC774': true,
    '\uB728\uC774': true, '\uB728\uC774': true, '\uB728\uC774': true, '\uB728\uC774': true, '\uB72F\uC5B4\uBC8C\uC774': true, '\uB9DE\uB193\uC774': true,
    '\uB9DE\uBC14\uB77C\uBCF4\uC774': true, '\uB9DE\uBD99\uC774': true, '\uB9DE\uC544\uB4E4\uC774': true, '\uB9DE\uCABC\uC774': true, '\uB9E1\uC774': true,
    '\uB9E4\uC190\uBD99\uC774': true, '\uB9E4\uC774': true, '\uB9E4\uC774': true, '\uB9E4\uC774': true, '\uB9E4\uC870\uC774': true, '\uBA39\uC774': true,
    '\uBA54\uB2E4\uBD99\uC774': true, '\uBA54\uBD99\uC774': true, '\uBA54\uC5B4\uBD99\uC774': true, '\uBA54\uC774': true, '\uBA85\uC528\uBC15\uC774': true,
    '\uBAA8\uC544\uB4E4\uC774': true, '\uBAA8\uC774': true, '\uBAB0\uC544\uB4E4\uC774': true, '\uBAB0\uC544\uBD99\uC774': true, '\uBB34\uC774': true, '\uBB36\uC774': true,
    '\uBB3C\uB4E4\uC774': true, '\uBB3C\uC5B4\uB4E4\uC774': true, '\uBBF8\uC774': true, '\uBC00\uC5B4\uBD99\uC774': true, '\uBC00\uCE58\uC774': true, '\uBC09\uBCF4\uC774': true,
    '\uBC14\uAFB8\uC774': true, '\uBC14\uB77C\uBCF4\uC774': true, '\uBC15\uC774': true, '\uBC15\uC774': true, '\uBC1B\uC544\uB4E4\uC774': true, '\uBC1C\uBCF4\uC774': true,
    '\uBC1C\uBD99\uC774': true, '\uBC29\uC774': true, '\uBC2D\uC774': true, '\uBC2D\uC774': true, '\uBC30\uAF2C\uC774': true, '\uBC30\uBD99\uC774': true,
    '\uBC30\uBD99\uC774': true, '\uBC88\uAC08\uC544\uB4E4\uC774': true, '\uBC8B\uB193\uC774': true, '\uBC8C\uC5B4\uB4E4\uC774': true, '\uBC8C\uC774': true, '\uBCA0\uC774': true,
    '\uBCF4\uC774': true, '\uBCF4\uC774': true, '\uBCF4\uC7C1\uC774': true, '\uBCF4\uCC44\uC774': true, '\uBCF6\uC774': true, '\uBD80\uB52A\uCE58\uC774': true,
    '\uBD80\uB808\uB053\uC774': true, '\uBD80\uB9AC\uC774': true, '\uBD80\uCE58\uC774': true, '\uBD88\uB7EC\uB4E4\uC774': true, '\uBD88\uBD99\uC774': true, '\uBD99\uB3D9\uC774': true,
    '\uBD99\uB9E4\uC774': true, '\uBD99\uBC15\uC774': true, '\uBD99\uC774': true, '\uBE44\uAF2C\uC774': true, '\uBE44\uB6A4\uC774': true, '\uBE44\uCD94\uC774': true,
    '\uBE57\uB193\uC774': true, '\uBE57\uBCF4\uC774': true, '\uBE68\uC544\uB4E4\uC774': true, '\uBED7\uC7A5\uC774': true, '\uC090\uB6A4\uC774': true, '\uC0AC\uB4E4\uC774': true,
    '\uC0AC\uC774': true, '\uC0AD\uC774': true, '\uC0AD\uC774': true, '\uC0DD\uCCAD\uBD99\uC774': true, '\uC11D\uC774': true, '\uC11E\uC774': true, '\uC120\uB4E4\uC774': true,
    '\uC120\uBCF4\uC774': true, '\uC124\uC8FD\uC774': true, '\uC18D\uC774': true, '\uC219\uC774': true, '\uC228\uC8FD\uC774': true, '\uC26C\uC774': true, '\uC2F8\uC774': true,
    '\uC2F8\uC774': true, '\uC313\uC774': true, '\uC369\uC774': true, '\uC3D8\uC544\uBD99\uC774': true, '\uC3D8\uC774': true, '\uC3D8\uC774': true, '\uC3F4\uBD99\uC774': true,
    '\uC4F0\uC774': true, '\uC4F0\uC774': true, '\uC4F0\uC774': true, '\uC4F0\uC774': true, '\uC54C\uC544\uBC29\uC774': true, '\uC560\uBA39\uC774': true,
    '\uC57C\uCF54\uC8FD\uC774': true, '\uC595\uBCF4\uC774': true, '\uC5B4\uB179\uC774': true, '\uC5BC\uB179\uC774': true, '\uC5BC\uBCF4\uC774': true, '\uC5BD\uB3D9\uC774': true,
    '\uC5BD\uB9E4\uC774': true, '\uC5BD\uC11E\uC774': true, '\uC5C7\uAE4E\uC774': true, '\uC5C7\uB204\uC774': true, '\uC5C7\uBC14\uAFB8\uC774': true, '\uC5C7\uBCA0\uC774': true,
    '\uC5C7\uBD99\uC774': true, '\uC5C7\uC11E\uC774': true, '\uC5CE\uC774': true, '\uC5D0\uC6CC\uC2F8\uC774': true, '\uC5D0\uC774': true, '\uC5EE\uC774': true,
    '\uC5F4\uC5B4\uBD99\uC774': true, '\uC5FF\uBCF4\uC774': true, '\uC625\uC774': true, '\uC625\uC870\uC774': true, '\uC625\uC8C4\uC774': true, '\uC62C\uB824\uBD99\uC774': true,
    '\uC62D\uB9E4\uC774': true, '\uC634\uCE20\uB7EC\uB4E4\uC774': true, '\uC695\uBCF4\uC774': true, '\uC6B0\uB7EC\uB7EC\uBCF4\uC774': true, '\uC6B0\uC905\uC774': true, '\uC6B1\uC774': true,
    '\uC6B1\uC870\uC774': true, '\uC6B1\uC8C4\uC774': true, '\uC6C0\uCE20\uB7EC\uB4E4\uC774': true, '\uC73D\uC8C4\uC774': true, '\uC775\uC0AD\uC774': true,
    '\uC7A1\uC544\uB4E4\uC774': true, '\uC7A5\uAC00\uB4E4\uC774': true, '\uC7C1\uC774': true, '\uC808\uC774': true, '\uC811\uBD99\uC774': true, '\uC811\uCE58\uC774': true,
    '\uC815\uB4E4\uC774': true, '\uC815\uBD99\uC774': true, '\uC870\uC774': true, '\uC878\uC774': true, '\uC8C4\uC774': true, '\uC8FD\uC774': true, '\uC8FD\uC774': true,
    '\uC904\uC774': true, '\uC950\uC774': true, '\uC950\uC774': true, '\uC9C0\uC774': true, '\uC9D3\uBCF6\uC774': true, '\uC9D3\uC8FD\uC774': true, '\uC9DC\uC774': true,
    '\uCABC\uC774': true, '\uCABC\uC774': true, '\uCABC\uC774': true, '\uCB10\uC774': true, '\uCC28\uC774': true, '\uCC98\uB4E4\uC774': true, '\uCC98\uBA39\uC774': true,
    '\uCC98\uC7C1\uC774': true, '\uCCD0\uB2E4\uBCF4\uC774': true, '\uCD94\uC774': true, '\uCD95\uC774': true, '\uCDA9\uC774': true, '\uCE58\uBA39\uC774': true,
    '\uCE58\uC313\uC774': true, '\uCE58\uC774': true, '\uCE58\uC774': true, '\uCE58\uC774': true, '\uCE58\uC774': true, '\uCE58\uC774': true, '\uCE58\uC774': true,
    '\uCE58\uC774': true, '\uCF1C\uC774': true, '\uD2B8\uC774': true, '\uD30C\uC774': true, '\uD3B4\uC774': true, '\uD480\uC5B4\uBA39\uC774': true, '\uD560\uD034\uC774': true,
    '\uD565\uC774': true, '\uD565\uC774': true, '\uD5DB\uB193\uC774': true, '\uD5DB\uBCF4\uC774': true, '\uD5DB\uC9DA\uC774': true, '\uD5DD\uD074\uC774': true,
    '\uD640\uB77C\uB4E4\uC774': true, '\uD645\uC774': true, '\uD6CC\uB2E6\uC774': true, '\uD6CC\uB77C\uB4E4\uC774': true, '\uD6D1\uC774': true, '\uD718\uB36E\uC774': true,
    '\uD718\uC5B4\uBD99\uC774': true, '\uD729\uC2F8\uC774': true, '\uD758\uB808\uBD99\uC774': true, '\uD759\uB4E4\uC774': true, '\uD769\uC774': true, '\uD798\uB4E4\uC774': true,
    '\uBAA8\uC774': true
}

conjugator.not_p_irregular = {'\uD138\uC369\uC774\uC7A1': true, '\uB118\uACA8\uC7A1': true, '\uC6B0\uC811': true, '\uC785': true, '\uB9DE\uC811': true, '\uBB38\uC7A1': true, '\uB2E4\uC7A1': true, '\uAE4C\uB4A4\uC9D1': true, '\uBC30\uC881': true, '\uBAA9\uC7A1': true, '\uB044\uC9D1': true, '\uC7A1': true, '\uC634\uCF1C\uC7A1': true, '\uAC80\uC7A1': true, '\uB418\uC21C\uB77C\uC7A1': true, '\uB0B4\uC539': true, '\uBAA8\uC9D1': true, '\uB530\uC7A1': true, '\uC5C7\uC7A1': true, '\uAE4C\uC9D1': true, '\uACB9\uC9D1': true, '\uC904\uD1B5\uBF51': true, '\uBC84\uB974\uC9D1': true, '\uC9C0\uB974\uC7A1': true, '\uCD94\uCF1C\uC7A1': true, '\uC5C5': true, '\uB418\uC220\uB798\uC7A1': true, '\uB418\uC811': true, '\uC881\uB514\uC881': true, '\uB354\uC704\uC7A1': true, '\uB9D0\uC539': true, '\uB0B4\uBF51': true, '\uC9D1': true, '\uAC78\uBA38\uC7A1': true, '\uD718\uC5B4\uC7A1': true, '\uAFF0\uC785': true, '\uD669\uC7A1': true, '\uC5D0\uAD7D': true, '\uB0B4\uAD7D': true, '\uB530\uB77C\uC7A1': true, '\uB9DE\uB4A4\uC9D1': true, '\uB458\uB7EC\uC5C5': true, '\uB298\uC7A1': true, '\uB044\uC7A1': true, '\uC6B0\uADF8\uB824\uC7A1': true, '\uC5B4\uC90D': true, '\uC5B8\uAC78\uC785': true, '\uB4E4\uC774\uACF1': true, '\uAEF4\uC7A1': true, '\uACF1 \uC811': true, '\uD6D4\uCF1C\uC7A1': true, '\uB2A6\uCD94\uC7A1': true, '\uAC08\uC544\uC785': true, '\uCE5C\uC881': true, '\uD76C\uC9DC\uBF51': true, '\uB9C8\uC74C\uC7A1': true, '\uAC1C\uBBF8\uC7A1': true, '\uC634\uC539': true, '\uCE58\uC7A1': true, '\uADF8\uB7EC\uC7A1': true, '\uC6C0\uCF1C\uC7A1': true, '\uC539': true, '\uBE44\uC9D1': true, '\uAF3D': true, '\uC0B4\uC7A1': true, '\uC8C4\uC785': true, '\uC878\uC7A1': true, '\uAC00\uB824\uC7A1': true, '\uBF51': true, '\uAC77\uC5B4\uC7A1': true, '\uD5D0\uC7A1': true, '\uB3CC\uB77C\uC785': true, '\uB367\uC7A1': true, '\uC595\uC7A1': true, '\uB0AB\uC7A1': true, '\uBD80\uC5EC\uC7A1': true, '\uB9DE\uBD99\uC7A1': true, '\uAC78\uC785': true, '\uC8FC\uB984\uC7A1': true, '\uAC77\uC5B4\uC785': true, '\uBE4C\uBBF8\uC7A1': true, '\uAC1C\uC7A1': true, '\uAC89\uC7A1': true, '\uC548\uCAD1\uC7A1': true, '\uC881': true, '\uD798\uC785': true, '\uAC77\uC7A1': true, '\uBC14\uB974\uC9D1': true, '\uAC10\uC539': true, '\uC9D3\uC539': true, '\uC190\uC7A1': true, '\uD3EC\uC9D1': true, '\uBD99\uC7A1': true, '\uB0AE\uC7A1': true, '\uCC45\uC7A1': true, '\uACF1\uC7A1': true, '\uD749\uC7A1': true, '\uB4A4\uC9D1': true, '\uB561\uC7A1': true, '\uC5B4\uB9BC\uC7A1': true, '\uB367\uAEF4\uC785': true, '\uC218\uC90D': true, '\uB4A4\uC7A1': true, '\uAF2C\uC9D1': true, '\uC608\uAD7D': true, '\uB36E\uCCD0\uC7A1': true, '\uD5DB\uC7A1': true, '\uB418\uC539': true, '\uB0AE\uCD94\uC7A1': true, '\uB0A0\uD30C\uB78C\uC7A1': true, '\uD2C0\uC5B4\uC7A1': true, '\uD5E4\uC9D1': true, '\uB0A8\uC758\uB2EC\uC7A1': true, '\uBC14\uB85C\uC7A1': true, '\uD760\uC7A1': true, '\uD30C\uC7A1': true, '\uC5BC\uCD94\uC7A1': true, '\uC190\uAF3D': true, '\uC811': true, '\uCC28\uB824\uC785': true, '\uACE8\uB77C\uC7A1': true, '\uAC70\uBA38\uC7A1': true, '\uD6C4\uB824\uC7A1': true, '\uBA38\uC90D': true, '\uB109\uC7A5\uBF51': true, '\uC0AC\uB85C\uC7A1': true, '\uB367\uC785': true, '\uAEF4\uC785': true, '\uC5BC\uC785': true, '\uC6B0\uC9D1': true, '\uC124\uC7A1': true, '\uB2A6\uC7A1': true, '\uBE44\uC881': true, '\uACE0\uB974\uC7A1': true, '\uB54C\uB824\uC7A1': true, '\uB5BC\uC9D1': true, '\uB418\uC7A1': true, '\uD648\uCF1C\uC7A1': true, '\uB0B4\uACF1': true, '\uACF1\uC539': true, '\uBE7C\uC785': true, '\uB4E4\uC774\uAD7D': true, '\uC0C8\uC7A1': true, '\uC774\uB974\uC9D1': true, '\uB5A8\uCCD0\uC785': true};

conjugator.not_s_irregular = {'\uB0B4\uC19F': true, '\uBE57': true, '\uB4DC\uC19F': true, '\uBE44\uC6C3': true, '\uBE8F': true, '\uC0D8\uC19F': true, '\uBC97': true, '\uB4E4\uC774\uC6C3': true, '\uC19F': true, '\uB418\uBE8F': true, '\uBE7C\uC557': true, '\uBC27': true, '\uC560\uAE0B': true, '\uC9DC\uB4DC\uB77C\uC6C3': true, '\uC5B4\uADF8\uC19F': true, '\uB4E4\uC19F': true, '\uC53B': true, '\uBE68\uAC00\uBC97': true, '\uAE43': true, '\uBC8C\uAC70\uBC97': true, '\uC5C7': true, '\uB418\uBE7C\uC557': true, '\uC6C3': true, '\uC557': true, '\uD5D0\uBC97': true, '\uC6A9\uC19F': true, '\uB367\uC19F': true, '\uBC1C\uAC00\uBC97': true, '\uBED8\uAC70\uBC97': true, '\uB0A0\uC19F': true, '\uCE58\uC19F': true};

conjugator.not_d_irregular = {'\uB9DE\uBC1B': true, '\uB0B4\uB51B': true, '\uB0B4\uB9AC\uBC1B': true, '\uBC8B': true, '\uB4A4\uB2EB': true, '\uC8FC\uACE0\uBC1B': true, '\uACF5\uC5BB': true, '\uBB34\uB72F': true, '\uBB3C\uC5B4\uB72F': true, '\uC5EC\uB2EB': true, '\uADF8\uB7EC\uBB3B': true, '\uC787\uB2EB': true, '\uB367\uBB3B': true, '\uB418\uBC1B': true, '\uBED7': true, '\uC62C\uB9AC\uB2EB': true, '\uD5D0\uB72F': true, '\uB4E4\uC774\uB2EB': true, '\uD65C\uAC77': true, '\uAC89\uBB3B': true, '\uB2EB': true, '\uCC3D\uBC1B': true, '\uAC74\uB124\uBC1B': true, '\uBB3C\uC190\uBC1B': true, '\uB4E4\uC774\uBC1B': true, '\uAC15\uC694\uBC1B': true, '\uB0B4\uB9AC\uBC8B': true, '\uBC1B': true, '\uC774\uC5B4\uBC1B': true, '\uBD80\uB974\uAC77': true, '\uC751\uBC1B': true, '\uAC80\uB72F': true, '\uC778\uC815\uBC1B': true, '\uB0B4\uB824\uB51B': true, '\uB0B4\uC3DF': true, '\uB0B4\uB9AC\uBED7': true, '\uB108\uB984\uBC1B': true, '\uC138\uBC1B': true, '\uB0B4 \uB3CB': true, '\uB3CC\uB824\uBC1B': true, '\uC950\uC5B4\uB72F': true, '\uAEF4\uBB3B': true, '\uBCF8\uBC1B': true, '\uB4A4\uBC1B': true, '\uAC15\uC885\uBC1B': true, '\uB0B4\uB9AC\uB2EB': true, '\uB5A0\uBC1B': true, '\uD14C\uBC1B': true, '\uB0B4\uBC1B': true, '\uD760\uB72F': true, '\uB450\uB0A8\uBC1B': true, '\uCE58\uBC1B': true, '\uBD80\uB974\uB3CB': true, '\uB300\uBC1B': true, '\uC124\uAD73': true, '\uCC98\uB2EB': true, '\uC5BB': true, '\uB4E4\uC774\uB3CB': true, '\uB3CB': true, '\uC8C4\uBC1B': true, '\uC3DF': true, '\uC528\uBC1B': true, '\uB531\uC7A5\uBC1B': true, '\uCE58\uAC77': true, '\uBBFF': true, '\uCE58\uBC8B': true, '\uBC84\uB9BC\uBC1B': true, '\uBD81\uB3CB': true, '\uB51B': true, '\uCE58\uACE0\uBC1B': true, '\uC6B1\uAC77': true, '\uBB3C\uB824\uBC1B': true, '\uB72F': true, '\uC934\uB72F': true, '\uB118\uACA8\uBC1B': true, '\uC548\uBC1B': true, '\uB0B4\uBED7': true, '\uB0B4\uB9AC\uC3DF': true, '\uBC8B\uB51B': true, '\uB4A4\uBB3B': true, '\uBED7\uB51B': true, '\uCE58\uBED7': true, '\uCE58\uB2EB': true, '\uC904\uBC11\uAC77': true, '\uAD73': true, '\uB0B4\uB2EB': true, '\uB0B4\uB9BC\uBC1B': true};

conjugator.not_h_irregular = {'\uB4E4\uC774\uC88B': true, '\uD130\uB193': true, '\uC811\uC5B4\uB193': true, '\uC88B': true, '\uD480\uC5B4\uB193': true, '\uB0B4\uC313': true, '\uAF34\uC88B': true, '\uCE58\uC313': true, '\uBB3C\uC5B4\uB123': true, '\uC787\uB2FF': true, '\uB05D\uB2FF': true, '\uADF8\uB7EC\uB123': true, '\uBF55\uB193': true, '\uB0B3': true, '\uB0B4\uB9AC\uCC27': true, '\uD798\uB2FF': true, '\uB0B4\uB824\uB193': true, '\uC138\uB193': true, '\uB458\uB7EC\uB193': true, '\uB4E4\uB193': true, '\uB9DE\uCC27': true, '\uC7A1\uC544\uB123': true, '\uB3CC\uB77C\uC313': true, '\uB367\uC313': true, '\uAC08\uB77C\uB54B': true, '\uC8FC\uB193': true, '\uAC08\uB77C\uB193': true, '\uB4E4\uC774\uB2FF': true, '\uC9D1\uC5B4\uB123': true, '\uB2FF': true, '\uC758\uC88B': true, '\uB9C9\uB193': true, '\uB0B4\uB193': true, '\uB4E4\uC5EC\uB193': true, '\uC0AC\uB193': true, '\uC370\uB808\uB193': true, '\uC9D3\uCC27': true, '\uBC8B\uB193': true, '\uCC27': true, '\uCE68\uB193': true, '\uB4E4\uC774\uCC27': true, '\uB458\uB7EC\uC313': true, '\uD138\uC5B4\uB193': true, '\uB2F4\uC313': true, '\uB3CC\uB77C\uB193': true, '\uB418\uC7A1\uC544\uB123': true, '\uB04C\uC5B4\uB123': true, '\uB367\uB193': true, '\uB9DE\uB2FF': true, '\uCC98\uB123': true, '\uBE7B': true, '\uBEE5\uB193': true, '\uB0B4\uB9AC\uC313': true, '\uACF1\uB193': true, '\uC124\uB808\uBC1C\uB193': true, '\uC6B0\uACA8\uB123': true, '\uB193': true, '\uC218\uB193': true, '\uC368\uB123': true, '\uB110\uC5B4\uB193': true, '\uB36E\uC313': true, '\uC5F0\uB2FF': true, '\uD5DB\uB193': true, '\uB3CC\uB824\uB193': true, '\uB418\uC313': true, '\uC6B1\uC5EC\uB123': true, '\uC557\uC544\uB123': true, '\uC62C\uB824\uB193': true, '\uD5DB\uBC29\uB193': true, '\uB0A0\uC544\uB193': true, '\uB4A4\uB193': true, '\uC5C5\uC218\uB193': true, '\uAC00\uB85C\uB193': true, '\uB9DE\uB193': true, '\uD3B4\uB193': true, '\uB0B4\uCF1C\uB193': true, '\uC313': true, '\uB059\uC9DC\uB193': true, '\uB4E4\uC774\uC313': true, '\uACB9\uC313': true, '\uAE30\uCD94\uB193': true, '\uB123': true, '\uBD88\uC5B4\uB123': true, '\uB298\uC5B4\uB193': true, '\uAE01\uC5B4\uB193': true, '\uC5B4\uAE0B\uB193': true, '\uC55E\uB123': true, '\uB20C\uB7EC\uB193': true, '\uB54B': true, '\uB4E4\uC5EC\uC313': true, '\uBE57\uB193': true, '\uC0AC\uC774\uC88B': true, '\uB418\uB193': true, '\uD5DB\uBD88\uB193': true, '\uBAB0\uC544\uB123': true, '\uBA39\uB193': true, '\uBC00\uCCD0\uB193': true, '\uC0B4\uB2FF': true, '\uD53C\uC0C8\uB193': true, '\uBE7C\uB193': true, '\uD558\uCC28\uB193': true, '\uD2C0\uC5B4\uB123': true};

conjugator.not_l_euh_irregular = {'\uC6B0\uB7EC\uB974': true, '\uB530\uB974': true, '\uBD99\uB530\uB974': true, '\uB2A6\uCE58\uB974': true, '\uB2E4\uB2E4\uB974': true, '\uC787\uB530\uB974': true, '\uCE58\uB974': true};

conjugator.not_l_irregular = {};

conjugator.after_last_space = function(infinitive) {
    return infinitive.split(' ').reverse()[0];
};

conjugator.is_s_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return hangeul.match(infinitive.charAt(infinitive.length-1), '*', '*', '\u11BA') &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_s_irregular);
};


conjugator.is_l_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return hangeul.match(infinitive.charAt(infinitive.length-1), '*', '*', '\u11AF') &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_l_irregular);
}

conjugator.is_l_euh_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return hangeul.match(infinitive.charAt(infinitive.length-1), '\u1105', '\u3161', null) &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_l_euh_irregular);
};

conjugator.is_h_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return (hangeul.padchim(infinitive.charAt(infinitive.length-1)) == '\u11C2' ||
           infinitive.charAt(infinitive.length-1) == '\uB7EC') &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_h_irregular);
};

conjugator.is_p_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return hangeul.match(infinitive.charAt(infinitive.length-1), '*', '*', '\u11B8') &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_p_irregular);
};

conjugator.is_d_irregular = function(infinitive, regular) {
    if (regular) {
        return false;
    }
    return hangeul.match(infinitive.charAt(infinitive.length-1), '*', '*', '\u11AE') &&
           !(conjugator.after_last_space(infinitive) in conjugator.not_d_irregular);
};

conjugator.verb_types = {
    '\u3145 \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_s_irregular,
    '\u3139 \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_l_irregular,
    '\uB974 \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_l_euh_irregular,
    '\u314E \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_h_irregular,
    '\u3142 \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_p_irregular,
    '\u3137 \uBD88\uADDC\uCE59 \uB3D9\uC0AC (irregular verb)': conjugator.is_d_irregular
};

conjugator.verb_type = function(infinitive, regular) {
    if (regular) {
        return 'regular verb';
    }
    for (irregular_name in conjugator.verb_types) {
        func = conjugator.verb_types[irregular_name];
        if (func(conjugator.base(infinitive))) {
            return irregular_name;
        }
    }
    return 'regular verb';
}

conjugator.base = function(infinitive, regular) {
    if (infinitive.charAt(infinitive.length-1) == '\uB2E4') {
        return infinitive.substring(0, infinitive.length-1);
    } else {
        return infinitive;
    }
};

conjugator.base2 = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive, regular);

    if (infinitive == '\uC544\uB2C8') {
        infinitive = new hangeul.Geulja('\uC544\uB2C8');
        infinitive.hidden_padchim = true;
        return infinitive;
    }
    if (infinitive == '\uBD59') {
        return '\uBD48';
    }
    if (infinitive == '\uD478') {
        return '\uD37C';
    }
    new_infinitive = infinitive;
    if (conjugator.is_h_irregular(infinitive, regular)) {
        new_infinitive = conjugator.merge(infinitive.substring(0, infinitive.length-1) +
                                          hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                                                       hangeul.vowel(infinitive.charAt(infinitive.length-1))),
                                          '\uC774');
        conjugator.reasons.push('\u314E irregular (' + infinitive + ' -> ' + new_infinitive + ')');
    } else if (conjugator.is_p_irregular(infinitive, regular)) {
        // only some verbs get \u3157 (highly irregular)
        if (infinitive in {'\uBB3B\uC7A1': true} ||
            infinitive.charAt(infinitive.length-1) in {'\uB3D5': true, '\uACF1': true}) {
            new_vowel = '\u3157';
        } else {
            new_vowel = '\u315C';
        }
        new_infinitive = conjugator.merge(infinitive.substring(0, infinitive.length-1) +
                                          hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                                                       hangeul.vowel(infinitive.charAt(infinitive.length-1))),
                                          hangeul.join('\u110B', new_vowel))
        conjugator.reasons.push('\u3142 irregular (' + infinitive + ' -> ' + new_infinitive + ')');
    } else if (conjugator.is_d_irregular(infinitive, regular)) {
        new_infinitive = new hangeul.Geulja(infinitive.substring(0, infinitive.length-1) +
                                            hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                                            hangeul.vowel(infinitive.charAt(infinitive.length-1)),
                                             '\u11AF'));
        new_infinitive.original_padchim = '\u11AE';
        conjugator.reasons.push('\u3137 irregular (' + infinitive + ' -> ' + new_infinitive + ')');
    } else if (conjugator.is_s_irregular(infinitive, regular)) {
        new_infinitive = new hangeul.Geulja(infinitive.substring(0, infinitive.length-1) +
                                            hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                                            hangeul.vowel(infinitive.charAt(infinitive.length-1))));
        new_infinitive.hidden_padchim = true;
        conjugator.reasons.push('\u3145 irregular (' + infinitive + ' -> ' + new_infinitive + ' [hidden padchim])');
    }
    return new_infinitive;
};

conjugator.base3 = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive, regular);
    if (infinitive == '\uC544\uB2C8') {
        return '\uC544\uB2C8';
    }
    if (infinitive == '\uD478') {
        return '\uD478';
    }
    if (infinitive == '\uBD59') {
        return '\uBD48';
    }
    if (conjugator.is_h_irregular(infinitive, regular)) {
        return infinitive.substring(0, infinitive.length-1) +
               hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                            hangeul.vowel(infinitive.charAt(infinitive.length-1)))
    } else if (conjugator.is_p_irregular(infinitive, regular)) {
        return infinitive.substring(0, infinitive.length-1) +
               hangeul.join(hangeul.lead(infinitive.charAt(infinitive.length-1)),
                            hangeul.vowel(infinitive.charAt(infinitive.length-1))) + '\uC6B0';
    } else {
        return conjugator.base2(infinitive, regular);
    }
};

conjugator.declarative_present_informal_low = function(infinitive, regular, further_use) {
    infinitive = conjugator.base2(infinitive, regular);
    if (!further_use && ((infinitive.charAt(infinitive.length-1) == '\uC774' && !infinitive.hidden_padchim &&
                          !(infinitive in conjugator.regular_ees) || infinitive == '\uC544\uB2C8') ||
                        (regular && infinitive.charAt(infinitive.length-1) == '\uC774'))) {
        conjugator.reasons.push('\uC57C irregular');
        return infinitive + '\uC57C';
    }
    // \uB974 irregular
    if (regular && infinitive == '\uC774\uB974') {
        return '\uC77C\uB7EC';
    }
    if (conjugator.is_l_euh_irregular(infinitive, regular)) {
        new_base = infinitive.substring(0, infinitive.length-2) +
                   hangeul.join(hangeul.lead(infinitive[infinitive.length-2]),
                                hangeul.vowel(infinitive[infinitive.length-2]),
                                '\u11AF');
        if (infinitive.substring(infinitive.length-2, infinitive.length) in {'\uD478\uB974': true, '\uC774\uB974': true}) {
            new_base = new_base + hangeul.join('\u1105',
                                               hangeul.vowel(hangeul.find_vowel_to_append(new_base)))
            conjugator.reasons.push('irregular stem + ' + infinitive + ' -> ' + new_base);
            return infinitive + '\uB7EC';
        } else if (hangeul.find_vowel_to_append(infinitive.substring(0, infinitive.length-1)) == '\uC544') {
            new_base += '\uB77C'
            conjugator.reasons.push('\uB974 irregular stem change [' + infinitive + ' -> ' + new_base + ']');
            return new_base;
        } else {
            new_base += '\uB7EC';
            conjugator.reasons.push('\uB974 irregular stem change [' + infinitive + ' -> ' + new_base + ']');
            return new_base;
        }
    } else if (infinitive.charAt(infinitive.length-1) == '\uD558') {
        return conjugator.merge(infinitive, '\uC5EC');
    } else if (conjugator.is_h_irregular(infinitive, regular)) {
        return conjugator.merge(infinitive, '\uC774');
    }
    return conjugator.merge(infinitive, hangeul.find_vowel_to_append(infinitive));
};
conjugator.declarative_present_informal_low.conjugation = true;

conjugator.declarative_present_informal_high = function(infinitive, regular) {
    base = conjugator.base2(infinitive, regular);
    if ((base.charAt(base.length-1) == '\uC774' && !base.hidden_padchim &&
        !(base in conjugator.regular_ees)) ||
        base == '\uC544\uB2C8') {
        conjugator.reasons.push('\uC5D0\uC694 irregular')
        return base + '\uC5D0\uC694';
    }
    return conjugator.merge(conjugator.declarative_present_informal_low(infinitive, regular, true), '\uC694');
};
conjugator.declarative_present_informal_high.conjugation = true;

conjugator.declarative_present_formal_low = function(infinitive, regular) {
    if (conjugator.is_l_irregular(conjugator.base(infinitive), regular)) {
        return conjugator.drop_l_and_borrow_padchim(conjugator.base(infinitive, regular), '\uB294\uB2E4');
    }
    return conjugator.merge(conjugator.base(infinitive, regular), '\uB294\uB2E4');
};
conjugator.declarative_present_formal_low.conjugation = true;

conjugator.declarative_present_formal_high = function(infinitive, regular) {
    if (conjugator.is_l_irregular(conjugator.base(infinitive), regular)) {
        return conjugator.drop_l_and_borrow_padchim(conjugator.base(infinitive, regular), '\uC2B5\uB2C8\uB2E4');
    }
    return conjugator.merge(conjugator.base(infinitive, regular), '\uC2B5\uB2C8\uB2E4')
};
conjugator.declarative_present_formal_high.conjugation = true;

conjugator.past_base = function(infinitive, regular) {
    ps = conjugator.declarative_present_informal_low(infinitive, regular, true);
    if (hangeul.find_vowel_to_append(ps) == '\uC544') {
        return conjugator.merge(ps, '\uC558');
    } else {
        return conjugator.merge(ps, '\uC5C8');
    }
};
conjugator.past_base.conjugation = true;

conjugator.declarative_past_informal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.past_base(infinitive, regular), '\uC5B4');
};
conjugator.declarative_past_informal_low.conjugation = true;

conjugator.declarative_past_informal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.declarative_past_informal_low(infinitive, regular), '\uC694');
};
conjugator.declarative_past_informal_high.conjugation = true;

conjugator.declarative_past_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.past_base(infinitive, regular), '\uB2E4');
};
conjugator.declarative_past_formal_low.conjugation = true;

conjugator.declarative_past_formal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.past_base(infinitive, regular), '\uC2B5\uB2C8\uB2E4');
};
conjugator.declarative_past_formal_high.conjugation = true;

conjugator.future_base = function(infinitive, regular) {
    if (conjugator.is_l_irregular(conjugator.base(infinitive, regular))) {
        return conjugator.drop_l_and_borrow_padchim(conjugator.base3(infinitive, regular), '\uC744');
    }
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uC744');
};
conjugator.future_base.conjugation = true;

conjugator.declarative_future_informal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.future_base(infinitive, regular), ' \uAC70\uC57C');
};
conjugator.declarative_future_informal_low.conjugation = true;

conjugator.declarative_future_informal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.future_base(infinitive, regular), ' \uAC70\uC608\uC694');
};
conjugator.declarative_future_informal_high.conjugation = true;

conjugator.declarative_future_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.future_base(infinitive, regular), ' \uAC70\uB2E4');
};
conjugator.declarative_future_formal_low.conjugation = true;

conjugator.declarative_future_formal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.future_base(infinitive, regular), ' \uAC81\uB2C8\uB2E4');
};
conjugator.declarative_future_formal_high.conjugation = true;

conjugator.declarative_future_conditional_informal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.base(infinitive, regular), '\uACA0\uC5B4');
};
conjugator.declarative_future_conditional_informal_low.conjugation = true;

conjugator.declarative_future_conditional_informal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.base(infinitive, regular), '\uACA0\uC5B4\uC694');
};
conjugator.declarative_future_conditional_informal_high.conjugation = true;

conjugator.declarative_future_conditional_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.base(infinitive, regular), '\uACA0\uB2E4');
};
conjugator.declarative_future_conditional_formal_low.conjugation = true;

conjugator.declarative_future_conditional_formal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.base(infinitive, regular), '\uACA0\uC2B5\uB2C8\uB2E4');
};
conjugator.declarative_future_conditional_formal_high.conjugation = true;

conjugator.inquisitive_present_informal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.declarative_present_informal_low(infinitive, regular), '?');
};
conjugator.inquisitive_present_informal_low.conjugation = true;

conjugator.inquisitive_present_informal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.declarative_present_informal_high(infinitive, regular), '?');
};
conjugator.inquisitive_present_informal_high.conjugation = true;

conjugator.inquisitive_present_formal_low = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive, regular);
    if (conjugator.is_l_irregular(infinitive, regular)) {
        return conjugator.drop_l(infinitive, '\uB2C8?');
    }
    return conjugator.merge(infinitive, '\uB2C8?');
};
conjugator.inquisitive_present_formal_low.conjugation = true;

conjugator.inquisitive_present_formal_high = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive, regular);
    if (conjugator.is_l_irregular(infinitive, regular)) {
        return conjugator.drop_l_and_borrow_padchim(infinitive, '\uC2B5\uB2C8\uAE4C?');
    }
    return conjugator.merge(infinitive, '\uC2B5\uB2C8\uAE4C?');
};
conjugator.inquisitive_present_formal_high.conjugation = true;

conjugator.inquisitive_past_informal_low = function(infinitive, regular) {
    return conjugator.declarative_past_informal_low(infinitive, regular) + '?';
};
conjugator.inquisitive_past_informal_low.conjugation = true;

conjugator.inquisitive_past_informal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.declarative_past_informal_high(infinitive, regular), '?');
};
conjugator.inquisitive_past_informal_high.conjugation = true;

conjugator.inquisitive_past_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.past_base(infinitive, regular), '\uB2C8?');
};
conjugator.inquisitive_past_formal_low.conjugation = true;

conjugator.inquisitive_past_formal_high = function(infinitive, regular) {
    return conjugator.merge(conjugator.past_base(infinitive, regular), '\uC2B5\uB2C8\uAE4C?');
};
conjugator.inquisitive_past_formal_high.conjugation = true;

conjugator.imperative_present_informal_low = function(infinitive, regular) {
    return conjugator.declarative_present_informal_low(infinitive, regular);
};
conjugator.imperative_present_informal_low.conjugation = true;

conjugator.imperative_present_informal_high = function(infinitive, regular) {
    if (conjugator.is_l_irregular(conjugator.base(infinitive, regular))) {
        return conjugator.drop_l(conjugator.base3(infinitive, regular), '\uC138\uC694');
    }
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uC138\uC694');
};
conjugator.imperative_present_informal_high.conjugation = true;

conjugator.imperative_present_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.imperative_present_informal_low(infinitive, regular), '\uB77C');
};
conjugator.imperative_present_formal_low.conjugation = true;

conjugator.imperative_present_formal_high = function(infinitive, regular) {
    if (conjugator.is_l_irregular(conjugator.base(infinitive, regular))) {
        return conjugator.drop_l(conjugator.base3(infinitive, regular), '\uC2ED\uC2DC\uC624');
    }
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uC2ED\uC2DC\uC624');
};
conjugator.imperative_present_formal_high.conjugation = true;

conjugator.propositive_present_informal_low = function(infinitive, regular) {
    return conjugator.declarative_present_informal_low(infinitive, regular);
};
conjugator.propositive_present_informal_low.conjugation = true;

conjugator.propositive_present_informal_high = function(infinitive, regular) {
    return conjugator.declarative_present_informal_high(infinitive, regular);
};
conjugator.propositive_present_informal_high.conjugation = true;

conjugator.propositive_present_formal_low = function(infinitive, regular) {
    return conjugator.merge(conjugator.base(infinitive, regular), '\uC790');
};
conjugator.propositive_present_formal_low.conjugation = true;

conjugator.propositive_present_formal_high = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive);
    if (conjugator.is_l_irregular(infinitive, regular)) {
        return conjugator.drop_l_and_borrow_padchim(conjugator.base3(infinitive, regular), '\uC74D\uC2DC\uB2E4');
    }
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uC74D\uC2DC\uB2E4');
};
conjugator.propositive_present_formal_high.conjugation = true;

conjugator.connective_if = function(infinitive, regular) {
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uBA74');
};
conjugator.connective_if.conjugation = true;

conjugator.connective_and = function(infinitive, regular) {
    infinitive = conjugator.base(infinitive, regular);
    return conjugator.merge(conjugator.base(infinitive, regular), '\uACE0');
};
conjugator.connective_and.conjugation = true;

conjugator.nominal_ing = function(infinitive, regular) {
    return conjugator.merge(conjugator.base3(infinitive, regular), '\uC74C');
};
conjugator.nominal_ing.conjugation = true;

conjugator.conjugations = [];

for (f in conjugator) {
    if (f && conjugator[f].conjugation) {
        conjugator.conjugations.push(f);
    }
}

conjugator.display_conjugations = function(infinitive, regular, callback) {
    var both_regular_and_irregular = false;
    infinitive = conjugator.base(infinitive, regular);
    out = '';
    if (infinitive in conjugator.both_regular_and_irregular) {
        both_regular_and_irregular = true;
        out += '<dd class="warning">warning</dd>';
        out += '<dt>This verb has both regular and irregular forms.</dt>';
    }
    out += '<div class="conjugation"><dd>verb type</dd>';
    out += '<dt>' + conjugator.verb_type(infinitive, regular)
    if (both_regular_and_irregular) {
        out += ' <button id="form-change">view ' + (regular ? 'irregular' : 'regular') + ' form</button>';
    }
    out += '</dt></div>';
    for (conjugation in conjugator) {
        conjugator.reasons = [];
        if (conjugator[conjugation].conjugation) {
            out += '<div class="conjugation"><dd>' + conjugation.replace(/_/g, ' ') + '</dd>';
            var conjugated = conjugator[conjugation](infinitive, regular);
            var pron = pronunciation.get_pronunciation(conjugated);
            var romanized = romanization.romanize(pron);
            out += '<dt>' + conjugated + ' <button class="show-reasons">\u21B4</button></dt>';
            out += '<ul class="reasons">';
            out += '<li>pronunciation [' + (pron != conjugated ? (pron + ' / ') : '') + romanized + ']</li>';
            for (reason in conjugator.reasons) {
                out += '<li>' + conjugator.reasons[reason] + '</li>';
            }
            out += '</ul></div>';
        }
    }
    callback(out);
};

conjugator.each_conjugation = function(infinitive, regular, callback) {
    infinitive = conjugator.base(infinitive, regular);
    for (conjugation in conjugator) {
        conjugator.reasons = [];
        if (conjugator[conjugation].conjugation) {
            var r = {};
            r.type = 'conjugation';
            r.infinitive = infinitive + '\uB2E4';
            r.conjugation_name = conjugation.replace(/_/g, ' ');
            r.conjugated = conjugator[conjugation](infinitive, regular);
            r.pronunciation = pronunciation.get_pronunciation(r.conjugated);
            r.romanized = romanization.romanize(r.pronunciation);
            r.reasons = [];
            for (reason in conjugator.reasons) {
                r.reasons.push(conjugator.reasons[reason]);
            }
            callback(r);
        }
    }
};

conjugator.conjugate = function(infinitive, regular, callback) {
    var conjugations = [];
    conjugator.each_conjugation(infinitive, regular, function(result) {
        conjugations.push(result);
    });
    callback(conjugations);
};

conjugator.conjugate_json = function(infinitive, regular, callback) {
    conjugator.conjugate(infinitive, regular, function(result) {
        result.unshift({
            'type': 'both_regular_and_irregular',
            'value': conjugator.base(infinitive) in conjugator.both_regular_and_irregular
        });
        result.unshift({
            'type': 'verb_type',
            'value': conjugator.verb_type(infinitive, regular)
        });
        callback(JSON.stringify(result));
    });
};

// This will be incremented when the algorithm is modified so clients
// that have cached API calls will know that their cache is invalid
conjugator.version = 1;

var stemmer = {};

stemmer.iterate_chop_last = function(s) {
    possibles = [];
    for (var i=s.length-1; i > 0; i--) {
        possibles.push(s.substring(0, s.length-i));
    }
    possibles.push(s);
    return possibles;
};

stemmer.generate_stems = function(verb) {
    possibles = [];
    if (verb[verb.length-1] == '\uD574') {
        possibles.push([false, verb.substring(0, verb.length-1) + '\uD558']);
    }
    if (hangeul.vowel(verb[verb.length-1]) == '\u3155') {
        possibles.push([false, verb.substring(0, verb.length-1) +
                               hangeul.join(hangeul.lead(verb[verb.length-1]), '\u3163')]);
    }
    if (hangeul.vowel(verb[verb.length-1]) == '\u3150') {
        possibles.push([false, verb.substring(0, verb.length-1) +
                      hangeul.join(hangeul.lead(verb[verb.length-1]),
                                   hangeul.vowel(hangeul.find_vowel_to_append(verb.substring(0, verb.length-1))),
                                   '\u11C2')]);
    }
    possibles.push([false, verb.substring(0, verb.length-1) +
                           hangeul.join(hangeul.lead(verb[verb.length-1]), '\u3161')]);
    possibles.push([true, verb]);
    // try adding back in irregular disappearing padchims
    ['\u11AE', '\u11B8','\u11AF', '\u11BA', '\u1102'].forEach(function(padchim) {
        possibles.push([false, verb.substring(0, verb.length-1) +
                                hangeul.join(hangeul.lead(verb[verb.length-1]),
                                             hangeul.vowel(verb[verb.length-1]), padchim)]);
    });
    // remove padchim entirely
    possibles.push([false, verb.substring(0, verb.length-1) +
                           hangeul.join(hangeul.lead(verb[verb.length-1]),
                                        hangeul.vowel(verb[verb.length-1]))]);
    return possibles;
};

stemmer.stem = function(verb) {
    // remove all conjugators that return what was passed in
    var ignored_conjugations = {};
    for (var f in conjugator) {
        if (conjugator[f].conjugation && conjugator[f]('test') == 'test') {
            ignored_conjugations[f] = true;
        }
    }
    var possible_stems = stemmer.iterate_chop_last(verb);
    for (var i in possible_stems) {
        var possible_base_stem = possible_stems[i];
        var generated_stems = stemmer.generate_stems(possible_base_stem);
        for (var j in generated_stems) {
            original = generated_stems[j][0];
            possible_stem = generated_stems[j][1];
            for (var f in conjugator) {
                if (!conjugator[f].conjugation || (f in ignored_conjugations && original)) {
                    continue;
                }
                if (conjugator[f](possible_stem) == verb) {
                    return possible_stem + '\uB2E4';
                }
            }
        }
    }
};

stemmer.stem_lookup = function(phrase, select_by_stem, callback) {
    var spread_phrase = hangeul.spread(phrase);
    var order = [];
    var results = {};
    var called = 0;
    function add_results(new_results) {
        for (var i=0; i<new_results.length; i++) {
            var infinitive = new_results[i][0];
            var definition = new_results[i][1];
            if (order.indexOf(infinitive) == -1) {
                order.push(infinitive);
            }
            if (!(infinitive in results)) {
                results[infinitive] = [];
            }
            if (results[infinitive].indexOf(definition) == -1) {
                results[infinitive].push(definition);
            }
        }
        called++;
        if (called == spread_phrase.length) {
            return callback(order, results);
        }
    }
    for (var i=spread_phrase.length; i>=0; i--) {
        select_by_stem.all(spread_phrase.substr(0, i), function(err, rows) {
            add_results(rows.map(function(r) {
                return [r.infinitive, r.definition];
            }));
        });
    }
};

stemmer.base_forms = function(infinitive) {
    var base_forms = [];
    var fn = function(base) {
        [true, false].forEach(function(regular) {
            base_form = String(base(infinitive, regular));
            if (base_form && base_forms.indexOf(base_form) == -1 && base_forms.indexOf(base_form.substr(0, base_form.length-1)) == -1) {
                base_forms.push(base_form);
            }
        });
    };
    fn(conjugator.base);
    fn(conjugator.base2);
    fn(conjugator.base3);
    fn(conjugator.declarative_present_informal_low);
    fn(function(infinitive, regular) {
            var original_infinitive = infinitive;
            infinitive = infinitive.substr(0, infinitive.length-1);
            if (!regular) {
                return conjugator.drop_l(infinitive, '');
            }
            return infinitive;
        });
    fn(function(infinitive, regular) {
            var conjugated = conjugator.declarative_present_informal_high(
                infinitive,
                regular
            );
            return conjugated.substr(0, conjugated.length-1);
        });
    return base_forms;
}