function gradioApp() {
    const elems = document.getElementsByTagName('gradio-app')
    const gradioShadowRoot = elems.length == 0 ? null : elems[0].shadowRoot
    return !!gradioShadowRoot ? gradioShadowRoot : document;
}

let executed = false

/** @type {(() => void)[]} */

/**
 * @param {string} tab
 * @param {boolean} show
 */
function kohya_sd_webui__toggle_runner_button(tab, show) {
    gradioApp().getElementById(`kohya_sd_webui__${tab}_run_button`).style.display = show ? 'block' : 'none'
    gradioApp().getElementById(`kohya_sd_webui__${tab}_stop_button`).style.display = show ? 'none' : 'block'
}

window.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver((m) => {
        if (!executed && gradioApp().querySelector('#kohya_sd_webui__root')) {
            executed = true;

            /** @type {Record<string, string>} */
            const helps = kohya_sd_webui__help_map
            /** @type {string[]} */
            const all_tabs = kohya_sd_webui__all_tabs

            const initializeTerminalObserver = () => {
                const container = gradioApp().querySelector("#kohya_sd_webui__terminal_outputs")
                setInterval(async () => {
                    const res = await fetch('./internal/extensions/kohya-sd-scripts-webui/terminal/outputs', {
                        method: "POST",
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            output_index: container.children.length
                        }),
                    })
                    const obj = await res.json()
                    const isBottom = container.scrollHeight - container.scrollTop === container.clientHeight
                    for(const line of obj.outputs){
                        const el = document.createElement('div')
                        el.innerText = line
                        container.appendChild(el)
                    }
                    if(isBottom) container.scrollTop = container.scrollHeight
                }, 1000)
            }

            const checkProcessIsAlive = () => {
                setInterval(async () => {
                    const res = await fetch('./internal/extensions/kohya-sd-scripts-webui/process/alive')
                    const obj = await res.json()
                    for (const tab of all_tabs)
                        kohya_sd_webui__toggle_runner_button(tab, !obj.alive)

                }, 1000)
            }

            initializeTerminalObserver()
            checkProcessIsAlive()

            for (const tab of all_tabs)
                gradioApp().querySelector(`#kohya_sd_webui__${tab}_run_button`).addEventListener('click', () => kohya_sd_webui__toggle_runner_button(tab, false))

            for (const [k, v] of Object.entries(helps)) {
                el = gradioApp().getElementById(k)
                if (!el) continue
                el.title = v
            }
        }
    })
    observer.observe(gradioApp(), { childList: true, subtree: true })
})