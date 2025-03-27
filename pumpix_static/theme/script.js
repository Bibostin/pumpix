// setup runtime UI
document.addEventListener("DOMContentLoaded", () => {
    console.log('loaded DOM');

    const info_button = document.getElementById("info-button");
    const info_close_button = document.getElementById('info-close-button');
    const darkmode_button = document.getElementById("darkmode-button");
    const error_elm = document.getElementById('error-close-button');

    // if lsval for darkmode is set, and true, use darkmode
    if (localStorage.getItem("pumpix_darkmode_enabled") === "true"){
        setDarkMode();
        flipflop = true;
    }
    // otherwise, it either doesn't exist, or is set to false, use lightmode.
    else {
        localStorage.setItem("pumpix_darkmode_enabled", "false");
        removeDarkMode();
        flipflop = false;
    }
    function setDarkMode() {
        info_button.src="/pumpix_static/theme/icons/infowhite.png";
        darkmode_button.src="/pumpix_static/theme/icons/sun.png";
        localStorage.setItem("pumpix_darkmode_enabled", "true");
        document.documentElement.style.setProperty("--c-font", "#FFFFFF");
        document.documentElement.style.setProperty("--c-bg1",  "#292727");
        document.documentElement.style.setProperty("--c-bg2",  "#323436");
        document.documentElement.style.setProperty("--c-bg3",  "#FFFFFF");
    };

    function removeDarkMode() {
        info_button.src="/pumpix_static/theme/icons/infoblack.png";
        darkmode_button.src="/pumpix_static/theme/icons/moon.png";
        localStorage.setItem("pumpix_darkmode_enabled", "false");
        document.documentElement.style.setProperty("--c-font", "#1a1616");
        document.documentElement.style.setProperty("--c-bg1",  "#FFFFFF");
        document.documentElement.style.setProperty("--c-bg2",  "#a8acb3");
        document.documentElement.style.setProperty("--c-bg3",  "#000000");
    };


    // setup info button and usage
    info_button.addEventListener('click', function() {
        document.querySelector('.info').classList.remove('hidden');
    });
    info_close_button.addEventListener('click', function() {
        document.querySelector('.info').classList.add('hidden');
    });
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelector('.info').classList.add('hidden');
        }
    });

    if (error_elm) {
        // setup error button and usage
        error_elm.addEventListener('click', function() {
            document.querySelector('.error').classList.add('hidden');
        });
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                document.querySelector('.error').classList.add('hidden');
            }
        });
    }

    // setup draggable construct
    const draggable_elms = document.querySelectorAll('.draggable');
    draggable_elms.forEach(element => {
        element.addEventListener('mousedown', (event) => {
            let shiftX = event.clientX - element.getBoundingClientRect().left;
            let shiftY = event.clientY - element.getBoundingClientRect().top;
            const moveAt = (pageX, pageY) => {
                element.style.left = pageX - shiftX + 'px';
                element.style.top = pageY - shiftY + 'px';
            };
            moveAt(event.pageX, event.pageY);
            const onMouseMove = (event) => {
                moveAt(event.pageX, event.pageY);
            };
            document.addEventListener('mousemove', onMouseMove);
            element.addEventListener('mouseup', () => {
                document.removeEventListener('mousemove', onMouseMove);
                element.onmouseup = null;
            });
            element.ondragstart = () => false;
        });
    });

    // setup darkmode
    document.getElementById('darkmode-button').addEventListener('click', function (){
        flipflop? setDarkMode() : removeDarkMode();
        flipflop = !flipflop;
    });
});
