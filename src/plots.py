import plotly.graph_objects as go


def donut_chart(data):
    labels = ["Off track", "On track"]
    values = [data["off_track_percent"].values[0], 
                100 - data["off_track_percent"].values[0]]
    
    colors =  ['#ef626c', '#312f2f']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.65, marker_colors=colors)])
    fig.update_layout(width=800,
                        height=600)

    return fig


def bar_chart(data):

    x1 = data['time']
    x2 = data['velocity']

    trace1 = go.Figure([go.Bar(x=x1, y=x2,
                          marker=dict(color="rgba(82, 84, 102, 0.65)",
                               line=dict(color="rgba(82, 84, 102, 1.0)", width=1.75)))
             ])
        
             
    trace1.update_layout(height=500,width=800,
                        xaxis_title="Time", yaxis_title="Velocity")

    #trace1.update_traces(marker_color='#2b2d42', opacity=.8)

    g = go.FigureWidget(data=trace1,
                        layout=go.Layout(
                            barmode='overlay'
                        ))

    return g


def progress_bar_chart(data):

    # For graphing pourposes, we need totals out of 100
    df_total_vis = data.copy()
    df_total_vis["Consistency"] = 100
    total_consistency = df_total_vis

    fig = go.Figure()
    fig.add_trace( go.Bar(
                        name = "Consistnecy",
                        x = data["Consistency"],
                        y = data["Month"],
                        orientation = 'h',
                        marker=dict(color="rgba(53, 143, 128, 1.0)",
                                line=dict(color="rgba(3, 102, 102, 1.0)", width=1.75)))
                )

    fig.add_trace( go.Bar(
                    x=total_consistency["Consistency"],
                    y=total_consistency["Month"],
                    orientation='h', 
                    showlegend = False,
                    marker=dict(color="rgba(53, 143, 128, .10)")
                                #line=dict(color="rgba(0, 0, 0, 1.0)", width=1.75)))
                ))

    fig.add_vline(x=80, line_width=1.5, line_dash="dash", line_color="rgba(3, 102, 102, .8)")
                
    fig.update_layout(barmode='stack',
                        title="Workout consisntecy per month",
                        width=1100,
                        height=300,
                        xaxis_title="Consistency (%)",
                        yaxis_title="Month")
    fig.update_xaxes(range = [0,100])

    return fig