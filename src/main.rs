use leptos::prelude::*;

fn main() {
    mount_to_body(App);
}

#[component]
pub fn App() -> impl IntoView {
    let (task, task_w) = signal(Item::default());
    let (tasks, tasks_w) = signal(Vec::<Item>::new());
    let (counter, counter_w) = signal(0);

    let input_class = "block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm p-2 bg-gray-50 border cursor-pointer";
    let label_class = "block text-xs font-semibold text-gray-600 uppercase mb-1";

    let tc_options = vec![
        "O(1)", "O(log n)", "O(n)", "O(n log n)", 
        "O(n^2)", "O(n^3)", "O(2^n)", "O(n!)", "Other"
    ];

    let sorted_tasks = move || {
        let mut t = tasks.get();
        t.reverse();
        t
    };

    view! {
        <main class="min-h-screen bg-gray-100 py-10 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
            <div class="max-w-4xl mx-auto">
                <header class="mb-8 text-center">
                    <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">"LeetCode Log"</h1>
                </header>

                <div class="bg-white rounded-xl shadow-lg p-6 mb-10 border border-gray-200">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class=label_class>"Problem Title"</label>
                            <input type="text" class=input_class placeholder="e.g. 3Sum"
                                on:input=move|e| task_w.write().title = event_target_value(&e) />
                        </div>
                        <div>
                            <label class=label_class>"URL"</label>
                            <input type="text" class=input_class placeholder="leetcode.com/..."
                                on:input=move|e| task_w.write().url = event_target_value(&e) />
                        </div>

                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class=label_class>"Difficulty"</label>
                                <select class=input_class on:change=move|e| task_w.write().diff = event_target_value(&e)>
                                    <option value="">"Select"</option>
                                    <option value="Easy">"Easy"</option>
                                    <option value="Medium">"Medium"</option>
                                    <option value="Hard">"Hard"</option>
                                </select>
                            </div>
                            <div>
                                <label class=label_class>"Date"</label>
                                <input type="date" class=input_class 
                                    on:input=move|e| task_w.write().date = event_target_value(&e) />
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class=label_class>"Optimal TC"</label>
                                <select class=input_class on:change=move|e| task_w.write().op_tc = event_target_value(&e)>
                                    <option value="">"Select"</option>
                                    {tc_options.clone().into_iter().map(|tc| view! { <option value=tc>{tc}</option> }).collect::<Vec<_>>()} //wtf is this
                                </select>
                            </div>
                            <div>
                                <label class=label_class>"My TC"</label>
                                <select class=input_class on:change=move|e| task_w.write().my_tc = event_target_value(&e)>
                                    <option value="">"Select"</option>
                                    {tc_options.clone().into_iter().map(|tc| view! { <option value=tc>{tc}</option> }).collect::<Vec<_>>()} //ik what this is... but WHY is this
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class=label_class>"Duration"</label>
                                <input type="text" class=input_class placeholder="20m"
                                    on:input=move|e| task_w.write().dur = event_target_value(&e) />
                            </div>
                            <div>
                                <label class=label_class>"Exec Time"</label>
                                <input type="text" class=input_class placeholder="4ms"
                                    on:input=move|e| task_w.write().exec_t = event_target_value(&e) />
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-wrap gap-4 mt-6 bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" class="rounded text-orange-600 h-4 w-4"
                                on:change=move|e| task_w.write().opt = event_target_checked(&e) />
                            <span class="text-sm font-medium italic">"Optimal?"</span>
                        </label>
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" class="rounded text-green-600 h-4 w-4"
                                on:change=move|e| task_w.write().sol = event_target_checked(&e) />
                            <span class="text-sm font-medium italic">"Solved?"</span>
                        </label>
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" class="rounded text-blue-600 h-4 w-4"
                                on:change=move|e| task_w.write().rev = event_target_checked(&e) />
                            <span class="text-sm font-medium italic">"Needs Revision?"</span>
                        </label>
                    </div>

                    <button 
                        class="mt-6 w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-4 rounded-lg transition shadow-sm active:scale-[0.98]"
                        on:click=move |_| {
                            tasks_w.write().push(task.get());
                            counter_w.update(|c| *c += 1);
                            task_w.write().id = counter.get();
                        }
                    >
                        "Log Problem"
                    </button>
                </div>

                <div class="space-y-4">
                    <For
                        each=sorted_tasks
                        key=|t| t.id
                        children=move |t| {
                            let diff_color = match t.diff.to_lowercase().as_str() {
                                "easy" => "bg-green-100 text-green-700",
                                "medium" => "bg-yellow-100 text-yellow-700",
                                "hard" => "bg-red-100 text-red-700",
                                _ => "bg-gray-100 text-gray-700"
                            };

                            view! {
                                <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200 group transition hover:border-orange-300">
                                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                        <div class="flex-1">
                                            <div class="flex flex-wrap items-center gap-2 mb-2">
                                                <h3 class="text-lg font-bold text-gray-800 tracking-tight">{t.title.clone()}</h3>
                                                <span class=format!("px-2 py-0.5 rounded text-[10px] font-black uppercase shadow-sm {}", diff_color)>
                                                    {t.diff.clone()}
                                                </span>
                                                {if t.opt {
                                                    Some(view! { <span class="text-[10px] bg-blue-600 text-white px-2 py-0.5 rounded font-black uppercase">"OPTIMAL"</span> })
                                                } else { None }}
                                                {if t.sol {
                                                    Some(view! { <span class="text-[10px] bg-black text-white px-2 py-0.5 rounded font-black uppercase">"SOLVED"</span> })
                                                } else { 
                                                    Some(view! { <span class="text-[10px] bg-red text-white px-2 py-0.5 rounded font-black uppercase">"NOT SOLVED"</span> })
                                                 }}
                                            </div>
                                            
                                            <div class="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-y-1 gap-x-6 text-xs text-gray-500 mt-1">
                                                <span>"Opt: " <b class="text-gray-900 font-mono">{t.op_tc.clone()}</b></span>
                                                <span>"Mine: " <b class="text-gray-900 font-mono">{t.my_tc.clone()}</b></span>
                                                <span>"Time: " <b class="text-gray-900">{t.dur.clone()}</b></span>
                                                <span>"Speed: " <b class="text-gray-900">{t.exec_t.clone()}</b></span>
                                                <span class="italic font-medium text-gray-400">{t.date.clone()}</span>
                                            </div>
                                        </div>

                                        <a href=t.url.clone() target="_blank" 
                                           class="text-center px-4 py-2 text-xs font-bold bg-gray-50 text-gray-500 rounded border border-gray-200 hover:bg-orange-600 hover:text-white hover:border-orange-600 transition duration-200">
                                            "LINK ↗"
                                        </a>
                                    </div>
                                </div>
                            }
                        }
                    />
                </div>
            </div>
        </main>
    }
}

#[derive(Clone, Default, Debug)]
struct Item {
    id: u32,
    date: String,
    title: String,
    url: String,
    diff: String,
    op_tc: String,
    my_tc: String,
    opt: bool,
    dur: String,
    exec_t: String,
    sol: bool,
    rev: bool
}