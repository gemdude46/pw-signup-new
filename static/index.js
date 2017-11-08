function supportsTransitions() {
	var b = document.body || document.documentElement,
		s = b.style,
		p = 'transition';

	if (typeof s[p] == 'string') { return true; }

	// Tests for vendor specific prop
	var v = ['Moz', 'webkit', 'Webkit', 'Khtml', 'O', 'ms'];
	p = p.charAt(0).toUpperCase() + p.substr(1);

	for (var i=0; i<v.length; i++) {
		if (typeof s[v[i] + p] == 'string') { return true; }
	}

	return false;
}

var gui_open = false;

var fancy = true;

onload = function(){
	setTimeout(function(){ document.querySelector('center').style.opacity = '1'; }, 100);

	if (!fancy) return;
	if (!supportsTransitions()) return;
	if (function(){/*foobar*/}.toString().indexOf('*foobar*') == -1) return;
	
	var page = (function(){/*
	<img src="//www.prewired.org/img/scotlandcol2.png" id=logo class=dispobj alt="PREWIRED">
	<h1 class=dispobj>Sign up for Prewired</h1>
	<h3 class=dispobj>On DATE</h3>
	<div class=dispobj>Your name: <input type=text></div>
	<div class=dispobj id=button>I'm going to Prewired!</div>
	<a href="register" class=dispobj>First time? Please <span>register</span>.</a>
	<div id=ierr></div>
	*/}).toString();
	document.body.innerHTML = page.substring(page.indexOf('/*')+3, page.indexOf('*/')).replace("DATE", DATE);
	
	if (localStorage.getItem('name'))
	   document.querySelector('.dispobj > input').value = localStorage.getItem('name');
	
	setTimeout(function(){document.body.children[0].style.opacity = '1'},  300);
	setTimeout(function(){document.body.children[1].style.opacity = '1'},  600);
	setTimeout(function(){document.body.children[2].style.opacity = '1'},  900);
	setTimeout(function(){document.body.children[3].style.opacity = '1'}, 1200);
	setTimeout(function(){document.body.children[4].style.opacity = '1'}, 1500);
	setTimeout(function(){document.body.children[5].style.opacity = '1'}, 1800);
	
	document.getElementById('button').addEventListener('click', function(){
		if (gui_open) return;
		gui_open = true;
		var x = new XMLHttpRequest();
		x.open('GET', URI + '?name=' + encodeURIComponent(document.querySelector('.dispobj > input').value), true);
		x.onreadystatechange = function(){
			if (x.readyState == 4) {
				var o = JSON.parse(x.responseText);
				if (o.status == 'success') {
					localStorage.setItem('name', document.querySelector('.dispobj > input').value);
					for (var i = 1; i < 6; i++)
						document.body.children[i].style.opacity = '0';
					setTimeout(function(){
						var h1 = document.querySelector('h1.dispobj');
						h1.innerHTML = 'You\'re going to Prewired!';
						h1.style.opacity = '1';
					}, 1000);
				} else {
					document.querySelector('#ierr').innerHTML = o.err + '<br><br><button>Ok</button>';
					document.querySelector('#ierr').style.bottom = '60%';
					document.querySelector('#ierr > button').addEventListener('click', function(){
						document.querySelector('#ierr').style.bottom = '120%';
						setTimeout(function(){
							gui_open = false;
						}, 1000);
					});
				}
			}
		}
		x.send(null);
	});
};
