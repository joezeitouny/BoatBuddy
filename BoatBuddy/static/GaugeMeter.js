/*
 * AshAlom Gauge Meter.  Version 2.0.0
 * Copyright AshAlom.com  All rights reserved.
 * https://github.com/AshAlom/GaugeMeter <- Deleted!
 * https://github.com/githubsrinath/GaugeMeter <- Backup original.
 *
 * Original created by Dr Ash Alom
 *
 * This is a bug fixed and modified version of the AshAlom Gauge Meter.
 * Copyright 2023 Michael Wolf (Mictronics)
 * https://github.com/mictronics/GaugeMeter
 *
 */
!(function ($) {
  $.fn.gaugeMeter = function (t) {
    var defaults = $.extend(
      {
        id: '',
        percent: 0,
        used: null,
        min: null,
        total: null,
        size: 100,
        prepend: '',
        append: '',
        theme: 'Red-Gold-Green',
        color: '',
        back: 'RGBa(0,0,0,.06)',
        width: 3,
        style: 'Full',
        stripe: '0',
        animationstep: 1,
        animate_gauge_colors: false,
        animate_text_colors: false,
        label: '',
        label_color: 'Black',
        text: '',
        text_size: 0.22,
        fill: '',
        showvalue: false,
        middle_value_format: false
      },
      t
    );
    return this.each(function () {
      function getThemeColor(e) {
        var t = '#2C94E0';
        return (
          e || (e = 1e-14),
          'Red-Gold-Green' === option.theme &&
            (e > 0 && (t = '#dc3545'),
            e > 10 && (t = '#e3443b'),
            e > 20 && (t = '#ea5331'),
            e > 30 && (t = '#f06127'),
            e > 40 && (t = '#f7701e'),
            e > 50 && (t = '#fd7e14'),
            e > 60 && (t = '#b98127'),
            e > 70 && (t = '#848336'),
            e > 80 && (t = '#4f8545'),
            e > 90 && (t = '#198754')),
          'Green-Gold-Red' === option.theme &&
             (e > 0 && (t = '#198754'),
             e > 10 && (t = '#4f8545'),
             e > 20 && (t = '#848336'),
             e > 30 && (t = '#b98127'),
             e > 40 && (t = '#fd7e14'),
             e > 50 && (t = '#f7701e'),
             e > 60 && (t = '#f06127'),
             e > 70 && (t = '#ea5331'),
             e > 80 && (t = '#e3443b'),
             e > 90 && (t = '#dc3545')),
          'Green-Red' === option.theme &&
            (e > 0 && (t = '#32d900'),
            e > 10 && (t = '#41c900'),
            e > 20 && (t = '#56b300'),
            e > 30 && (t = '#6f9900'),
            e > 40 && (t = '#8a7b00'),
            e > 50 && (t = '#a75e00'),
            e > 60 && (t = '#c24000'),
            e > 70 && (t = '#db2600'),
            e > 80 && (t = '#f01000'),
            e > 90 && (t = '#ff0000')),
          'Red-Green' === option.theme &&
            (e > 0 && (t = '#ff0000'),
            e > 10 && (t = '#f01000'),
            e > 20 && (t = '#db2600'),
            e > 30 && (t = '#c24000'),
            e > 40 && (t = '#a75e00'),
            e > 50 && (t = '#8a7b00'),
            e > 60 && (t = '#6f9900'),
            e > 70 && (t = '#56b300'),
            e > 80 && (t = '#41c900'),
            e > 90 && (t = '#32d900')),
          'DarkBlue-LightBlue' === option.theme &&
            (e > 0 && (t = '#2c94e0'),
            e > 10 && (t = '#2b96e1'),
            e > 20 && (t = '#2b99e4'),
            e > 30 && (t = '#2a9ce7'),
            e > 40 && (t = '#28a0e9'),
            e > 50 && (t = '#26a4ed'),
            e > 60 && (t = '#25a8f0'),
            e > 70 && (t = '#24acf3'),
            e > 80 && (t = '#23aff5'),
            e > 90 && (t = '#21b2f7')),
          'LightBlue-DarkBlue' === option.theme &&
            (e > 0 && (t = '#21b2f7'),
            e > 10 && (t = '#23aff5'),
            e > 20 && (t = '#24acf3'),
            e > 30 && (t = '#25a8f0'),
            e > 40 && (t = '#26a4ed'),
            e > 50 && (t = '#28a0e9'),
            e > 60 && (t = '#2a9ce7'),
            e > 70 && (t = '#2b99e4'),
            e > 80 && (t = '#2b96e1'),
            e > 90 && (t = '#2c94e0')),
          'DarkRed-LightRed' === option.theme &&
            (e > 0 && (t = '#d90000'),
            e > 10 && (t = '#dc0000'),
            e > 20 && (t = '#e00000'),
            e > 30 && (t = '#e40000'),
            e > 40 && (t = '#ea0000'),
            e > 50 && (t = '#ee0000'),
            e > 60 && (t = '#f30000'),
            e > 70 && (t = '#f90000'),
            e > 80 && (t = '#fc0000'),
            e > 90 && (t = '#ff0000')),
          'LightRed-DarkRed' === option.theme &&
            (e > 0 && (t = '#ff0000'),
            e > 10 && (t = '#fc0000'),
            e > 20 && (t = '#f90000'),
            e > 30 && (t = '#f30000'),
            e > 40 && (t = '#ee0000'),
            e > 50 && (t = '#ea0000'),
            e > 60 && (t = '#e40000'),
            e > 70 && (t = '#e00000'),
            e > 80 && (t = '#dc0000'),
            e > 90 && (t = '#d90000')),
          'DarkGreen-LightGreen' === option.theme &&
            (e > 0 && (t = '#198754'),
            e > 10 && (t = '#1c995f'),
            e > 20 && (t = '#20aa6a'),
            e > 30 && (t = '#23bc75'),
            e > 40 && (t = '#26ce80'),
            e > 50 && (t = '#30d98b'),
            e > 60 && (t = '#42dc95'),
            e > 70 && (t = '#54df9f'),
            e > 80 && (t = '#65e3a9'),
            e > 90 && (t = '#77e6b3')),
          'LightGreen-DarkGreen' === option.theme &&
            (e > 0 && (t = '#77e6b3'),
            e > 10 && (t = '#65e3a9'),
            e > 20 && (t = '#54df9f'),
            e > 30 && (t = '#42dc95'),
            e > 40 && (t = '#30d98b'),
            e > 50 && (t = '#26ce80'),
            e > 60 && (t = '#23bc75'),
            e > 70 && (t = '#20aa6a'),
            e > 80 && (t = '#1c995f'),
            e > 90 && (t = '#198754')),
          'Green-Gold' === option.theme &&
            (e > 0 && (t = '#198754'),
            e > 10 && (t = '#34844C'),
            e > 20 && (t = '#518445'),
            e > 30 && (t = '#6D843C'),
            e > 40 && (t = '#848436'),
            e > 50 && (t = '#9B842F'),
            e > 60 && (t = '#B88428'),
            e > 70 && (t = '#CF8424'),
            e > 80 && (t = '#E97D19'),
            e > 90 && (t = '#fd7e14')),
          'Gold-Green' === option.theme &&
            (e > 0 && (t = '#fd7e14'),
            e > 10 && (t = '#E97D19'),
            e > 20 && (t = '#CF8424'),
            e > 30 && (t = '#B88428'),
            e > 40 && (t = '#9B842F'),
            e > 50 && (t = '#848436'),
            e > 60 && (t = '#6D843C'),
            e > 70 && (t = '#518445'),
            e > 80 && (t = '#34844C'),
            e > 90 && (t = '#198754')),
          'White' === option.theme && (t = '#fff'),
          'Black' === option.theme && (t = '#000'),
          t
        );
      }
      /* The label below gauge. */
      function createLabel(t, a) {
        if (t.children('b').length === 0) {
          $('<b></b>')
            .appendTo(t)
            .html(option.label)
            .css({
              'line-height': option.size + 5 * a + 'px',
//              color: option.label_color
            });
        }
      }
      /* Prepend and append text, the gauge text or percentage value. */
      function createSpanTag(t) {
        var fgcolor = '';
        if (option.animate_text_colors === true) {
          fgcolor = option.fgcolor;
        }
        var child = t.children('span');
        if (child.length !== 0) {
          child.html(r).css({ color: fgcolor });
          return;
        }
        if (option.text_size <= 0.0 || Number.isNaN(option.text_size)) {
          option.text_size = 0.22;
        }
        if (option.text_size > 0.5) {
          option.text_size = 0.5;
        }
        $('<span></span>')
          .appendTo(t)
          .html(r)
          .css({
            'line-height': option.size + 'px',
            'font-size': option.text_size * option.size + 'px',
            color: fgcolor
          });
      }
      /* Get data attributes as options from div tag. Fall back to defaults when not exists. */
      function getDataAttr(t) {
        $.each(dataAttr, function (index, element) {
          if (t.data(element) !== undefined && t.data(element) !== null) {
            option[element] = t.data(element);
          } else {
            option[element] = $(defaults).attr(element);
          }

          if (element === 'fill') {
            s = option[element];
          }

          if (
            (element === 'size' ||
              element === 'width' ||
              element === 'animationstep' ||
              element === 'stripe') &&
            !Number.isInteger(option[element])
          ) {
            option[element] = parseInt(option[element]);
          }

          if (element === 'text_size') {
            option[element] = parseFloat(option[element]);
          }
        });
      }
      /* Draws the gauge. */
      function drawGauge(a) {
        if (M < 0) M = 0;
        if (M > 100) M = 100;
        var lw =
          option.width < 1 || isNaN(option.width)
            ? option.size / 20
            : option.width;
        g.clearRect(0, 0, b.width, b.height);
        g.beginPath();
        g.arc(m, v, x, G, k, !1);
        if (s) {
          g.fillStyle = option.fill;
          g.fill();
        }
        g.lineWidth = lw;
        g.strokeStyle = option.back;
        option.stripe > parseInt(0)
          ? g.setLineDash([option.stripe], 1)
          : (g.lineCap = 'round');
        g.stroke();

        if (option.middle_value_format) {
            // Draw a line from the center to the specified value
            g.beginPath();
            startAngle = 0;
            endAngle = 0
            if (a <= 0.5) {
                startAngle = P * a - I;
                endAngle = P * 0.5 - I;
            } else {
                startAngle = P * 0.5 - I;
                endAngle = P * a - I;
            }
            g.arc(m, v, x, startAngle, endAngle, !1);
            g.lineWidth = lw;
            g.strokeStyle = option.fgcolor;
            g.stroke();
        } else {
            g.beginPath();
            g.arc(m, v, x, -I, P * a - I, !1);
            g.lineWidth = lw;
            g.strokeStyle = option.fgcolor;
            g.stroke();
        }

        // Highlight Circle
        g.beginPath();
        g.arc(m, v, x, P * a - I, P * a - I,!1);
        g.lineWidth = lw + 5;
        g.strokeStyle = option.fgcolor;
        g.stroke();

        c > M &&
          ((M += z),
          requestAnimationFrame(function () {
            drawGauge(Math.min(M, c) / 100);
            console.log(M, c);
            if (defaults.showvalue === true || option.showvalue === true) {
              $(p).find('output').text(option.used);
            } else {
              $(p).find('output').text(M);
            }
          }, p));
      }

      $(this).attr('data-id', $(this).attr('id'));
      var r,
        dataAttr = [
          'percent',
          'used',
          'min',
          'total',
          'size',
          'prepend',
          'append',
          'theme',
          'color',
          'back',
          'width',
          'style',
          'stripe',
          'animationstep',
          'animate_gauge_colors',
          'animate_text_colors',
          'label',
          'label_color',
          'text',
          'text_size',
          'fill',
          'showvalue',
          'middle_value_format'
        ],
        option = {},
        c = 0,
        p = $(this),
        s = false;
      p.addClass('gaugeMeter');
      getDataAttr(p);

      if (Number.isInteger(option.total)) {
        var u = option.used;
        var t = option.total;
        if (Number.isInteger(option.min)) {
          if (option.min < 0) {
            t -= option.min;
            u -= option.min;
          }
        }
        c = u / (t / 100);
      } else {
        if (Number.isInteger(option.percent)) {
          c = option.percent;
        } else {
          c = parseInt(defaults.percent);
        }
      }
      if (c < 0) c = 0;
      if (c > 100) c = 100;

      if (
        option.text !== '' &&
        option.text !== null &&
        option.text !== undefined
      ) {
        if (
          option.append !== '' &&
          option.append !== null &&
          option.append !== undefined
        ) {
          r = option.text + '<u>' + option.append + '</u>';
        } else {
          r = option.text;
        }
        if (
          option.prepend !== '' &&
          option.prepend !== null &&
          option.prepend !== undefined
        ) {
          r = '<s>' + option.prepend + '</s>' + r;
        }
      } else {
        if (defaults.showvalue === true || option.showvalue === true) {
          r = '<output>' + option.used + '</output>';
        } else {
          r = '<output>' + c.toString() + '</output>';
        }
        if (
          option.prepend !== '' &&
          option.prepend !== null &&
          option.prepend !== undefined
        ) {
          r = '<s>' + option.prepend + '</s>' + r;
        }

        if (
          option.append !== '' &&
          option.append !== null &&
          option.append !== undefined
        ) {
          r = r + '<u>' + option.append + '</u>';
        }
      }

      option.fgcolor = getThemeColor(c);
      if (
        option.color !== '' &&
        option.color !== null &&
        option.color !== undefined
      ) {
        option.fgcolor = option.color;
      }

      if (option.animate_gauge_colors === true) {
        option.fgcolor = getThemeColor(c);
      }
      createSpanTag(p);

      if (
        option.style !== '' &&
        option.style !== null &&
        option.style !== undefined
      ) {
        createLabel(p, option.size / 13);
      }

      $(this).width(option.size + 'px');

      var b = $('<canvas></canvas>')
          .attr({ width: option.size, height: option.size })
          .get(0),
        g = b.getContext('2d'),
        m = b.width / 2,
        v = b.height / 2,
        _ = 360 * option.percent,
        x = (_ * (Math.PI / 180), b.width / 2.5),
        k = 2.3 * Math.PI,
        G = 0,
        M = 0 === option.animationstep ? c : 0,
        z = Math.max(option.animationstep, 0),
        P = 2 * Math.PI,
        I = Math.PI / 2,
        R = option.style;
      var child = $(this).children('canvas');
      if (child.length !== 0) {
        /* Replace existing canvas when new percentage was written. */
        child.replaceWith(b);
      } else {
        /* Initially create canvas. */
        $(b).appendTo($(this));
      }

      if ('Semi' === R) {
        k = 2 * Math.PI;
        G = 3.13;
        P = 1 * Math.PI;
        I = Math.PI / 0.996;
      }
      if ('Arch' === R) {
        k = 2.195 * Math.PI;
        (G = 1), (G = 655.99999);
        P = 1.4 * Math.PI;
        I = Math.PI / 0.8335;
      }
      drawGauge(M / 100);
    });
  };
})(jQuery);
