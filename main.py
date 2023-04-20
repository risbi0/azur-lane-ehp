import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title='Azur Lane eHP',
    layout='wide',
    menu_items={
        'About': '''
            ##### Azur Lane eHP

            Data and calculations from Mebot#6604 and website made by Risbiantotri#9712.
        '''
    }
)

st.markdown(
    '''
    <style>
        ul[aria-activedescendant] ul[role="option"]:nth-child(n+3):nth-child(-n+7),
        ul[aria-activedescendant] div:nth-child(n+1):nth-child(-n+5),
        div[data-testid="stDecoration"], iframe, footer {
            display: none !important;
        }
        .main .block-container {
            padding-top: 40px;
        }
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
            display: none !important;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown('<h4>Vanguard eHP</h4>', unsafe_allow_html=True)
st.caption('Data is colored by armor type. (Green: Light, Orange: Medium, Heavy: Red). Value is the average eHP between 13 enemies. See [below](#documentation) for a detailed explanation.')

def ordinal_suffix(n):
    if n % 100 in (11, 12, 13):
        return 'th'
    else:
        return { 1: 'st', 2: 'nd', 3: 'rd' }.get(n % 10, 'th')

df = pd.read_csv('data/vg.csv', index_col=[0])

armor_colors = {
    'light': '#86b341',
    'medium': '#e3a949',
    'heavy': '#ff5858',
}

cols = st.columns(4)
armor_type = cols[1].selectbox('Armor Type:', ['All', 'Light', 'Medium', 'Heavy'])
hull_type = cols[2].selectbox('Hull Type:', ['All', 'DD', 'CL', 'CA', 'CB', 'AE'])

if armor_type != 'All':
    df = df[df['armor'] == armor_type]
if hull_type != 'All':
    df = df[df['hull'] == hull_type]

if len(df) >= 10:
    height = round(len(df) * 21.5)
elif len(df) <= 9 and len(df) >= 2:
    height = round(len(df) * 50)
elif len(df) == 1:
    height = 75

if len(df) > 0:
	counter = len(df)
	fig = go.Figure()

	for row in df.iterrows():
		name = row[1]['name']
		ehp = row[1]['ehp']
		armor = row[1]['armor'].lower()
		hull = row[1]['hull'].lower()

		fig.add_trace(
			go.Bar(
				x=[ehp],
				y=[name],
				orientation='h',
				text=ehp,
				textposition='outside',
				hovertemplate=f'{counter}{ordinal_suffix(counter)}, {name}, {ehp}',
				marker=dict(color=armor_colors[armor]),
				showlegend=False,
				name=''
			)
		)

		counter -= 1

	fig.update_layout(
		legend=dict(x=1, xanchor='right', y=0),
		margin=dict(l=0, r=0, t=50, b=0),
		height=height,
		xaxis=dict(visible=False, range=[0, 35000])
	)

	fig.update_xaxes(fixedrange=True)

	cols = st.columns([1, 3, 1])
	cols[1].plotly_chart(fig, use_container_width=True)
else:
     st.text('No data available.')

documentation = r'''
$eHP$ is calculated using the equations present [here](https://azurlane.koumakan.jp/wiki/Combat#Evasion_and_Accuracy) as the center of the theory.

$$
\begin{align*}
Accuracy = &\ 0.1 + \frac{AttackerHit}{AttackerHit + DefenderEvasion + 2} +\\
& \frac{AttackerLuck - DefenderLuck + LevelDifference}{1000} +\\
&AccuracyVsShipTypeSkill - EvasionRateSkill
\end{align*}
$$

This is a number between 0.1 and 1, meaning that the minimum accuracy any ship can have against any other is just a 10% accuracy. Conversely, the maximum accuracy any ship can have against any other is 100% accuracy - a perfect hitrate.

For any particular amount of $HP$ that a ship has, you can calculate the eHP of a ship by dividing its $HP$ by the measure of $Accuracy$.

$$
eHP = \frac{HP}{Accuracy}
$$

We are calculating the $eHP$ of allied ships, and so the “attacker” in this case is literally any enemy ever. As it is, we haven't found any enemy with an $AccuracyVsShipTypeSkill$, so we'll remove that from the $Accuracy$ equation.

$$
ACC = 0.1 +
\frac{AtkHIT}{AtkHIT + DefEVA + 2} +
\frac{AtkLCK - DefLCK + LvlDiff}{1000} -
EVARate
$$

This gives us a new $eHP$ equation.

$$
eHP =
\frac{HP}
{0.1 +
\frac{AtkHIT}{AtkHIT + DefEVA + 2} +
\frac{AtkLCK - DefLCK + LvlDiff}{1000} -
EVARate}
$$

Level 120 stats are taken from [here](https://azurlane.koumakan.jp/wiki/List_of_Ships_by_Stats), and input into the equation. We can
figure out $HP$, $DefEVA$, $DefLCK$, and $EVARate$, but we can not find out $ATKHit$, $AtkLCK$, or $LvlDIFF$ without knowing
what the enemy is. These stats are taken from [here](https://i.imgur.com/9BWcy19.jpg), compiled by Arctic V#8978. Let us
handwave some stats based on what we see of the enemies.

$$
AtkHIT = 100
AtkLCK = 25
LvlDiff = 8
$$

This means that our enemies are level 128, and have $HIT = 100$ and $LCK = 25$. Let's calculate the eHP of a [Purin](https://azurlane.koumakan.jp/wiki/Prototype_Bulin_MKII) with no gear on, against this type of enemy.

$$
eHP =
\frac{232}
{0.1 +
\frac{100}{100 + 116 + 2} +
\frac{25 - 100 + 8}{1000}}
eHP = 471.817
$$

The most intuitive way someone can interpret this number is: "This is how much damage a ship can take before she sinks, including shots missed". Missed in this context is the text that appears over your ship when she “evades” a shot - meaning that the enemy failed their accuracy check.

But this interpretation itself has no solid meaning without producing some assumptions about the battle. So let's start with a basic, and reasonable assumption: "The battle lasts 90 seconds."

This is important for skills that are time-based, such as smokescreens, limited buffs, and even the Repair Toolkit's repairing skill.

If we pair the length of the battle with the intuitive meaning of the $eHP$ value, then we give a slightly different interpretation of this $eHP$ value: "In 90 seconds, if the ship takes any more damage than this number, including shots missed, she will die".

Actually, that's false. Half the time, she would take more damage upon death, and the other half the time, she would take less damage. This $eHP$ value is more accurate of the average damage that she would have taken upon death, so let us rephrase this interpretation: "In 90 seconds, this number is the average amount of damage the ship will take, including missed shots, before she dies".

This means that the weakest enemy with these stats that CAN reliably kill the Purin, needs to do at least 471.817 damage over the course of 90 seconds. So, in a manner, this interpretation of $eHP$ is a measure of how strong the weakest enemies need to be, in order to kill her. The bigger the number, the stronger the enemy needs to be to reliably kill her.

Now, we may include auxiliary equipment into the calculation. For most purposes, auxiliary equipment provides $HP$ and $EVA$ stats that will augment the ship's $eHP$. The equipment stats are taken from [here](https://azurlane.koumakan.jp/wiki/List_of_Auxiliary_Equipment#Max_Stats-0).

For DD's, I chose the Repair Toolkit and a 550 HP auxiliary equipment as normal gears to consider.

For CL's and CA's, I chose the Repair Toolkit and Improved Hydraulic Rudder as normal gears to consider.

For CB's, I allowed two versions. Both have Improved Hydraulic Rudder, and then either Repair Toolkit or VH Armor.

For AE's, I gave them three equipment: Repair Toolkit, Improved Hydraulic Rudder, and a 500 HP auxiliary equipment.

All instances of Improved Hydraulic Rudder are in their +13 configuration.

So, for this Purin example, let's give her some DD equipment.

Her new $HP$ value is $232 + 500 + 550 = 1282$. But wait! The Repair Toolkit restores 1% max $HP$ every 15s. So, 1% additional $HP$ is given at $t = 15,30,45,60,75$. Meaning that any ship that has a Repair Toolkit will have 105% of her nominal $HP$!

So her new HP value is actually $(232 + 500 + 550)(1 + 0.05) = 1346.1$.

Now, we divide by the accuracy value (unchanged because neither equipment gave $EVA$).

$$
eHP =
\frac{1346.1}
{0.1 +
\frac{100}{100 + 116 + 2} +
\frac{25 - 100 + 8}{1000}}
$$
$$
eHP = 2737.558
$$

Let's calculate the $eHP$ of a slightly (a lot) more complicated setup: 120 [Chikuma](https://azurlane.koumakan.jp/wiki/Chikuma) with Improved Hydraulic Rudder and Repair Toolkit.

Let's take a look at her skills - pivotal to her $eHP$ is the "All-Obscuring Eye", which gives her 10% $EVARate$ whenever she is slow. She has 20% Damage Reduction, and can have her $EVA$ boosted by 20%. So her $eHP$ currently looks like this:

$$
eHP =
\frac{1}{1 - 0.2}
\frac{(4392 + 500 + 72)(1 + 0.05)}
{0.1 +
\frac{100}{100 + (75 + 49)(1 + 0.2) + 2} +
\frac{25 - 42 + 8}{1000} - 0.1}
= 16594.863
$$

The fraction in front is However, it would be wrong to apply all of these buffs to her $eHP$ at once, because the uptime for each of these buffs is not 100%.

So, we take a look at when she is slowed, and push a reasonable guess as to how many seconds total she is slowed. "All-Seeing Eye" procs 5 times, and gives her 15s of slowness. "All-Obscuring Eye's" effect has a cooldown of 10s, but you shouldn't expect it to proc after exactly 10s. This is where we guess up a reasonable number, and say that it actually takes 2s to proc - for 12s between procs in total. This allows for 7 procs, which means 49s of slow.

Thus, her 10% $EVARate$ is active whenever she is slowed, $15s + 49s = 64s$. So, her average $EVARate$ is $10\% × \frac{64s}{90s} = 7.11%$.

Similarly, her 20% $EVABoost$ is active for 49s. So, her average $EVABoost$ is $20\% × 49s 90s = 10.9%$.

So, we can update her $eHP$ to be this:

$$
eHP =
\frac{1}{1 - 0.02}
\frac{(4392 + 500 + 72)(1 + 0.05)}
{0.1 +
\frac{100}{100 + (75 + 49)(1 + 0.2 (\frac{49}{90})) + 2} +
\frac{25 - 42 + 8}{1000} - 0.1
(\frac{64}{90})}
= 14787.782
$$

Now, we're almost done. The last thing to consider is the Improved Hydraulic Rudder's skill. On seconds 20, 40, 60, and 80, we have a 30% chance to be invulnerable for 2s. We take an average again, which looks like 30% of 8s. We are treating invulnerability as 100% damage reduction. Normally, this would result in the ship being invulnerable, but we only have 100% damage reduction for 30% of 8s. So, the average damage reduction value is $100\% × \frac{30\% × 8s}{90s} = 2.667\%$. This is the final correction we need to do to grab Chikuma's $eHP$:

$$
eHP =
\frac{1}{1 - 0.0267}
\frac{1}{1 - 0.02}
\frac{(4392 + 500 + 72)(1 + 0.05)}
{0.1 +
\frac{100}{100 + (75 + 49)(1 + 0.2 (\frac{49}{90})) + 2} +
\frac{25 - 42 + 8}{1000} - 0.1
(\frac{64}{90})}
= 15193.447
$$

But we're not done yet. (This is not the final number you see on the website.) Depending on the bullet that hits the shipgirl, she may take more or less damage. This is usually seen in an $X/Y/Z$ format, where $X$ is the multiplier to damage done to $Light$ armored targets, Y is the multiplier for Medium armored targets, and $Z$ is the multiplier for Heav armored targets. In this case, our shipgirls are the targets for the bullets fired by the enemies. Enemy bullet modifiers are taken from [here](https://i.imgur.com/pdQxbBT.png).

For example, against Defense Module: Chaser III has 1/0.8/0.4, 0.8/1/1.3, and 0.9/1/1.2 modifier bullets. (Chikuma's nominal $eHP$ against this is 16417.202, her $eHP$ against those three bullets will be, respectively, 20521.503, 16417.202, and 16417.202. How do we determine Chikuma's true $eHP$ when she has three, against this boss?

Sadly, your regular average (17785.302) will not cut it. The reasoning is - if there was a bullet that did 1/0/1 damage, Chikuma's $eHP$ would be the average of 20521.503, 16417.202, 16417.202, and $\infty$. That's also $\infty$, which is wrong, because the other bullets do deal damage, and therefore this boss can kill Chikuma. Having an $eHP$ of $\infty$ means she can not die. This is a contradiction, so the regular average can not be used here. The proper average to use is called the "harmonic average", which looks like this:

$$
\frac{1}{eHP} =
\frac{p_1}{eHP_1} +
\frac{p_2}{eHP_2} +
\frac{p_3}{eHP_3} +
... +
\frac{p_n}{eHP_n}
$$

Where $p_i$ is the probability of a bullet encountering the shipgirl with $eHP_2$. Let's work with a simple example. The shipgirl has a nominal $eHP$ of 10000, and the enemy has two bullets fired in equal volumes. One is 1/1/1, and the other is 0/0/0.

Each bullet has a 50% chance of being either bullet, so $p_1$ and $p_2$ are 50%. $eHP_1$ is 10000, and $eHP_2$ is $\infty$. The resultant harmonic average is:

$$
\frac{1}{eHP} =
\frac{0.1}{10000} +
\frac{0.5}{\infty} =
\frac{1}{20000}
$$
$$
eHP = 20000
$$

This means that the enemy needs to shoot 20000 bullets to kill the shipgirl. This makes sense, as half of those bullets will do 0 damage, and the other half will deal 10000 damage. This equips us with an averaging system that properly gives 0's and $\infty$'s the treatment they deserve.

So, back to Chikuma, this means that her $eHP$ against Defense Module: Chaser III is:

$$
\frac{1}{eHP} =
\frac{1/3}{20521.503} +
\frac{1/3}{16417.202} +
\frac{1/3}{16417.202}
$$
$$
eHP = 17589.859
$$

BUT! This is still not yet the final number we see on the chart. THAT one is a regular average of all the $eHP$'s of the different bosses we see in Operation Siren. Namely: Defense Module: Chaser III, Defense Module: Navigator III, Defense Module: Smasher III, Defense Module: Conductor, Enforcer XIV [Equilibrium], Enforcer IX [Concealment], Enforcer VII [Determination], Enforcer IX [Exploration], Enforcer XIV [Harmony], Arbiter: Temperance XIV, Arbiter: The Hermit IX, Arbiter: Strength VIII, and Repulse META.

I don't have the other META's on here, because I am too lazy to datamine their bullets.

The reason why we use the regular average for the $eHP$ between the different boss types is because a shipgirl does not fight multiple bosses at once. When one boss uses multiple different types of bullets, they're coming at the shipgirl all at once - which necessitates the harmonic average. So, the $eHP$'s of Chikuma are:
'''

example_df = pd.DataFrame({
     'Enemy': ['Defense Module: Chaser III', 'Defense Module: Navigator III', 'Defense Module: Smasher III', 'Defense Module: Conductor', 'Enforcer XIV [Equilibrium]', 'Enforcer IX [Concealment]', 'Enforcer VII [Determination]', 'Enforcer IX [Exploration]', 'Enforcer XIV [Harmony]', 'Arbiter: Temperance XIV', 'Arbiter: The Hermit IX', 'Arbiter: Strength VIII', ' Repulse META'],
     'eHP': [17589.859, 18535.551, 20613.289, 23745.112, 16482.738, 20757.724, 22579.732, 15615.225, 19468.106, 13641.840, 15767.204, 16717.180, 13248.258]
})
example_df['eHP'] = example_df['eHP'].round(3)

cols = st.columns([1, 4, 1])
cols[1].subheader('Documentation')
cols[1].write(documentation)
cols[1].write(example_df.to_html(index=False), unsafe_allow_html=True)
cols[1].write('The arithmetic average of all of these values are 18058.602, which is the number shown in the chart.')
