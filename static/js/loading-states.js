/**
 * Gestion des états de chargement (loading states)
 * Améliore l'expérience utilisateur avec des indicateurs visuels
 * 
 * NOTE: SCRIPT ENTIÈREMENT DÉSACTIVÉ TEMPORAIREMENT pour éviter la page blanche et l'animation
 * L'actualisation automatique continue de fonctionner sans ces éléments visuels
 */

// ========== TOUT LE CODE CI-DESSOUS EST DÉSACTIVÉ TEMPORAIREMENT ==========

/*
// Afficher un spinner de chargement sur les boutons lors des soumissions de formulaire
document.addEventListener('DOMContentLoaded', function() {
    // Intercepter tous les formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                // Désactiver le bouton
                submitButton.disabled = true;
                
                // Ajouter un spinner si ce n'est pas déjà fait
                if (!submitButton.querySelector('.spinner-border')) {
                    const originalText = submitButton.innerHTML;
                    submitButton.dataset.originalText = originalText;
                    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Chargement...';
                }
            }
        });
    });
    
    // Intercepter les liens avec confirmation ou actions importantes
    const actionLinks = document.querySelectorAll('a[href*="supprimer"], a[href*="delete"], a[href*="terminer"]');
    actionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.dataset.loading) {
                this.dataset.loading = 'true';
                const originalText = this.innerHTML;
                this.dataset.originalText = originalText;
                this.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> ' + originalText;
                this.style.pointerEvents = 'none';
            }
        });
    });
    
    // Gestion du chargement des pages - DÉSACTIVÉ TEMPORAIREMENT
    window.addEventListener('beforeunload', function() {
        // Afficher un overlay de chargement
        const loader = document.createElement('div');
        loader.id = 'page-loader';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        loader.innerHTML = `
            <div style="text-align: center;">
                <div id="lottie-container" style="width: 250px; height: 250px; margin: 0 auto; display: none;"></div>
                <img id="gif-fallback" src="/static/images/home.gif" alt="Chargement" style="width: 250px; height: 250px; object-fit: contain; display: block; animation: pulse 2s ease-in-out infinite;" />
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.8; transform: scale(1.05); }
                }
            </style>
        `;
        // Essayer de charger l'animation Lottie, sinon utiliser le GIF
        if (typeof lottie !== 'undefined') {
            try {
                lottie.loadAnimation({
                    container: loader.querySelector('#lottie-container'),
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    path: '/static/images/home.json'
                });
            } catch(e) {
                loader.querySelector('#lottie-container').style.display = 'none';
                loader.querySelector('#gif-fallback').style.display = 'block';
            }
        } else {
            loader.querySelector('#lottie-container').style.display = 'none';
            loader.querySelector('#gif-fallback').style.display = 'block';
        }
        document.body.appendChild(loader);
    });
});
*/

// Fonction utilitaire pour afficher un loader sur un élément - DÉSACTIVÉE
/*
function showLoader(element) {
    if (element) {
        element.style.position = 'relative';
        const loader = document.createElement('div');
        loader.className = 'element-loader';
        loader.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        loader.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>';
        element.appendChild(loader);
    }
}

// Fonction utilitaire pour masquer un loader - DÉSACTIVÉE
function hideLoader(element) {
    if (element) {
        const loader = element.querySelector('.element-loader');
        if (loader) {
            loader.remove();
        }
    }
}
*/

// Gestion du chargement pour les requêtes AJAX - DÉSACTIVÉ TEMPORAIREMENT
/*
const originalFetch = window.fetch;
window.fetch = function(...args) {
    // Afficher un loader global pour les requêtes longues
    const loader = document.getElementById('page-loader') || createGlobalLoader();
    loader.style.display = 'flex';
    
    return originalFetch.apply(this, args)
        .finally(() => {
            setTimeout(() => {
                loader.style.display = 'none';
            }, 300);
        });
};
*/

// Fonction createGlobalLoader - DÉSACTIVÉE TEMPORAIREMENT
/*
function createGlobalLoader() {
    const loader = document.createElement('div');
    loader.id = 'page-loader';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        z-index: 9999;
        display: none;
        align-items: center;
        justify-content: center;
    `;
    loader.innerHTML = `
        <div style="text-align: center;">
            <div id="lottie-container-global" style="width: 250px; height: 250px; margin: 0 auto; display: none;"></div>
            <img id="gif-fallback-global" src="/static/images/home.gif" alt="Chargement" style="width: 250px; height: 250px; object-fit: contain; display: block; animation: pulse 2s ease-in-out infinite;" />
        </div>
        <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.8; transform: scale(1.05); }
            }
        </style>
    `;
    // Essayer de charger l'animation Lottie, sinon utiliser le GIF
    if (typeof lottie !== 'undefined') {
        try {
            lottie.loadAnimation({
                container: loader.querySelector('#lottie-container-global'),
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: '/static/images/home.json'
            });
        } catch(e) {
            loader.querySelector('#lottie-container-global').style.display = 'none';
            loader.querySelector('#gif-fallback-global').style.display = 'block';
        }
    } else {
        loader.querySelector('#lottie-container-global').style.display = 'none';
        loader.querySelector('#gif-fallback-global').style.display = 'block';
    }
    document.body.appendChild(loader);
    return loader;
}
*/

