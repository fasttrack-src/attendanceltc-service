// Filter function for course view.
function filterCourses()
{
	var input = $("#filter-courses-department").val().toLowerCase();
	console.log("result is" + input);

	$('#courses-department > tbody > tr').each(function() {
		var courseid = $(this).find('td[id*=id]').html().toLowerCase();
		var name = $(this).find('td[id*=name]').html().toLowerCase();
		
		if(courseid.includes(input) || name.includes(input)) {
			$(this).show();
		} else {
			$(this).hide();
		}
	});
}