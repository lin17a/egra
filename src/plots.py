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


def line_chart(data):
    # plotly figure with go object plotting 2 lines
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['i'], y=data['value_x'], name='Gen 1',
                        line=dict(color='#EF626C', width=2)))
    fig.add_trace(go.Scatter(x=data['i'], y=data['value_y'], name='Gen 2',
                        line=dict(color='#84DCCF', width=2)))

    fig.update_layout(width=1000,
                        height=600,
                        xaxis_title="Iteration",
                        yaxis_title="Value")
    return fig