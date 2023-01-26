function gradioApp() {
    const elems = document.getElementsByTagName('gradio-app')
    const gradioShadowRoot = elems.length == 0 ? null : elems[0].shadowRoot
    return !!gradioShadowRoot ? gradioShadowRoot : document;
}
let executed = false
window.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver((m) => {
        if(!executed && gradioApp().querySelector('#kohya_sd_webui__root')){
            executed = true;
            /** @type {Record<string, string>} */
            const helps = kohya_sd_webui__help_map

            for (const [k, v] of Object.entries(helps)) {
                el = gradioApp().getElementById(k)
                if (!el) continue
                el.title = v
            }
        }
    })
    observer.observe(gradioApp(), { childList: true, subtree: true })
})