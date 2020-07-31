function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function stripCurrency(currency) {
    return currency.replace('$', '').replace(',', '');
}

function formatNumber(number) {
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    });
    return formatter.format(number);
}

function currencyToNumber(currency) {
    return Number(stripCurrency(currency));
}

(function ( $ ) {
    $.fn.currencyFormat = function( options ) {
        var el = $(this);
        var val = el.val();
		el.val(formatNumber(currencyToNumber(val)));

		el.change(function(event) {
			var val = $(this).val();
			$(this).val(formatNumber(currencyToNumber(val)));
		});
    };
}( jQuery ));

(function ( $ ) {
    $.fn.passwordStrengthMeter = function( options ) {
        var strength = {
            0: "Worst",
            1: "Bad",
            2: "Weak",
            3: "Good",
            4: "Strong"
        }
        
        $(this).on('input', function() {
            var text = document.getElementById('password-strength-text');
            var meter = document.getElementById('password-strength-meter');

            var result = zxcvbn(this.value);
            meter.value = result.score;

            if (this.value !== "") {
                text.innerHTML = strength[result.score]; 
            } else {
                text.innerHTML = "";
            }
        });
    };
}( jQuery ));
